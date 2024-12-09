import asyncio
import json
import logging
import urllib
import urllib.parse
from datetime import datetime, timezone
from time import sleep
from typing import Any, AsyncIterator, Callable

import aiofiles
import numpy as np
import requests
import websockets
from pydantic import BaseModel
from scipy.sparse import spmatrix
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def loki_ready(address: str = "localhost:3100"):
    url = f"http://{address}/ready"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        logging.fatal(
            "Loki instance not ready:"
            f"\n\tStatus code: `{response.status_code}`"
            f"\n\tContent: `{response.content}`"
        )
        return False
    except requests.exceptions.RequestException as ex:
        logging.fatal(f"Error connecting to Loki\n{ex}")


class LokiResponseStream(BaseModel):
    stream: dict[str, str]
    values: list[list[str]]


async def stream_logs(
    query: str = r'{__log_source=~".+"}',
    delay_for: int = 0,
    limit: int = 100,
    address: str = "localhost:3100",
) -> AsyncIterator[LokiResponseStream]:
    uri = f"ws://{address}/loki/api/v1/tail"
    params = {
        "query": query,
        "delay_for": delay_for,
        "limit": limit,
    }
    param_str = "&".join(
        f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items()
    )
    async with websockets.connect(f"{uri}?{param_str}") as websocket:
        logging.warning("Streaming logs...")
        async for message in websocket:
            streams = json.loads(message).get("streams", [])

            for stream in streams:
                stream_data = LokiResponseStream.model_validate(stream)
                yield stream_data


async def preprocess_logs(
    log_streams: AsyncIterator[LokiResponseStream],
) -> AsyncIterator[list[str]]:
    async for log_stream in log_streams:
        raw_logs = [value[1] for value in log_stream.values]
        yield raw_logs


async def clusterize_logs(logs_stream: AsyncIterator[list[str]]):
    tfidf_vectorizer = TfidfVectorizer()
    minibatch_kmeans = MiniBatchKMeans(
        n_clusters=10,
        random_state=np.random.RandomState(42),
        batch_size=100,
    )

    buffer: list[str] = []
    batch_counter = 0
    first_batch = True  # Flag to track the first batch
    batch_size_threshold = (
        100  # Number of batches to process before updating the vectorizer
    )

    async for logs in logs_stream:
        for log in logs:
            buffer.append(log)

        logging.info(f"Log line received ({len(buffer)}).")

        if len(buffer) >= batch_size_threshold:
            transformed_logs: spmatrix
            if first_batch:
                transformed_logs = tfidf_vectorizer.fit_transform(buffer)
                first_batch = False
            else:
                transformed_logs = tfidf_vectorizer.transform(buffer)

            batch_data = np.vstack(transformed_logs.toarray())  # type: ignore

            batch_data -= np.mean(batch_data, axis=0)
            batch_data /= np.std(batch_data, axis=0, ddof=0) + 1e-8

            minibatch_kmeans.partial_fit(batch_data)

            labels = minibatch_kmeans.predict(batch_data)

            clustered_logs = [
                {
                    "log": log,
                    "cluster": int(label),
                    "feature_vector": feature.tolist(),
                    "timestamp": datetime.now(timezone.utc),
                }
                for log, label, feature in zip(buffer, labels, batch_data)
            ]

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_file = f"./logs/pipeline/batch_{timestamp}_{batch_counter}.json"

            async with aiofiles.open(output_file, "a") as file:
                await file.write(json.dumps(clustered_logs, default=str))

            logging.info(f"Results for batch {batch_counter} written to {output_file}")
            batch_counter += 1

            buffer = []

            if batch_counter % 10 == 0:
                tfidf_vectorizer = TfidfVectorizer(
                    vocabulary=tfidf_vectorizer.vocabulary_
                )
                transformed_logs = tfidf_vectorizer.fit_transform(logs)

                logging.info("TfidfVectorizer vocabulary updated.")


async def log_processing_pipeline(
    stages: list[tuple[Callable, tuple[Any], dict[str, Any]]]
):
    if not stages:
        raise ValueError("Pipeline stages cannot be empty")

    # Initialize the first stage
    first_stage_func, first_args, first_kwargs = stages[0]
    result = first_stage_func(*first_args, **first_kwargs)

    # Connect the stages
    for stage_func, stage_args, stage_kwargs in stages[1:]:
        result = stage_func(result, *stage_args, **stage_kwargs)

    # Consume the final stage to ensure full execution
    await result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    while not loki_ready():
        logging.warning("Loki is not ready. Sleeping for 5 seconds...")
        sleep(5)

    pipeline_stages = [
        (stream_logs, (), {"query": r'{__log_source=~".+"}', "limit": 100}),
        (preprocess_logs, (), {}),
        (clusterize_logs, (), {}),
    ]

    asyncio.run(log_processing_pipeline(pipeline_stages))
