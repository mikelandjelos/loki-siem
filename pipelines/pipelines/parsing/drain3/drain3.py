import argparse
import csv
import logging
import os
import sys
from datetime import datetime
from os.path import dirname, exists, join
from time import perf_counter
from typing import Optional

import pandas as pd
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

from ...utils.functions import (
    csv_dict_generator,
    get_all_files_recursively,
    get_dataset_name,
)
from ...utils.metrics_monitor import MetricsMonitor

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

INPUT_DIR = join("results", "parsing", "preprocessing")

RESULTS_DIR = join("results", "parsing", "drain3")
METRICS_DIR = join("metrics", "parsing", "drain3")

BATCH_SIZE = 50000


def get_parser(parent_subparsers: Optional[argparse._SubParsersAction] = None):
    """Drain3 log parser."""
    parser = (
        argparse.ArgumentParser(description=get_parser.__doc__)
        if not parent_subparsers
        else parent_subparsers.add_parser("drain3", description=get_parser.__doc__)
    )

    parser.set_defaults(func=main)

    return parser


def main(args: Optional[argparse.Namespace] = None):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(METRICS_DIR, exist_ok=True)

    if not args:
        args = get_parser().parse_args()

    config_file = join(dirname(__file__), "drain3.ini")
    config = TemplateMinerConfig()
    config.load(config_file)
    # config.profiling_enabled = True

    metrics_gathered = []

    for input_file in get_all_files_recursively(INPUT_DIR):
        template_miner = TemplateMiner(config=config)
        dataset_name = get_dataset_name(input_file)

        if not exists(input_file):
            raise ValueError(f"Preprocessed log file `{input_file}` doesn't exist!")

        metrics_monitor = MetricsMonitor()

        log_count = 0
        batch = []
        result_file = join(RESULTS_DIR, f"{dataset_name}.csv")

        start = perf_counter()

        with open(result_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = None
            metrics_monitor.start()

            for structured_log in csv_dict_generator(input_file):
                content = structured_log["Content"]  # Unstructured
                structured_content = template_miner.add_log_message(content)

                structured_log["EventTemplate"] = structured_content["template_mined"]
                structured_log["Parameters"] = template_miner.get_parameter_list(
                    structured_log["EventTemplate"], content
                )

                del structured_log["Content"]
                batch.append(structured_log)

                if writer is None:
                    fieldnames = list(batch[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                log_count += 1

                if log_count % BATCH_SIZE == 0:
                    writer.writerows(batch)
                    batch = []

            if len(batch) > 0 and writer is not None:
                writer.writerows(batch)

            end = perf_counter()

            metrics_df = metrics_monitor.stop(log_count)
            metrics_df["Dataset"] = dataset_name
            metrics_df["Cluster Count"] = len(template_miner.drain.clusters)
            metrics_gathered.append(metrics_df)

            logger.info(
                f"Dataset `{dataset_name}` finished preprocessing at an "
                f"average rate of {log_count/(end-start)} [log/sec] - {log_count} logs in {end-start} seconds. "
                f"Cluster count: {len(template_miner.drain.clusters)}"
            )

    pd.concat(metrics_gathered, ignore_index=True).to_csv(
        join(METRICS_DIR, f"drain3_{datetime.now().isoformat()}.csv"),
        index=False,
    )


if __name__ == "__main__":
    main()
