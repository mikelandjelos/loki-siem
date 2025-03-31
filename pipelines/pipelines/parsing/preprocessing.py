import argparse
import csv
import logging
import os
import re
import sys
from datetime import datetime
from os.path import exists, join
from time import perf_counter
from typing import Optional

import pandas as pd

from ..utils.functions import get_dataset_name, log_generator
from ..utils.metrics_monitor import MetricsMonitor

RESULTS_DIR = join("results", "parsing", "preprocessing")
METRICS_DIR = join("metrics", "parsing", "preprocessing")
BATCH_SIZE = 10000

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")


def get_parser(parent_subparsers: Optional[argparse._SubParsersAction] = None):
    """Log parsing - preprocessing utility."""
    parser = (
        argparse.ArgumentParser(description=get_parser.__doc__)
        if not parent_subparsers
        else parent_subparsers.add_parser(
            "preprocessing", description=get_parser.__doc__
        )
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable testing mode",
    )

    dataset_choices = list(DATASET_PREPROCESSING_PARAMETERS.keys())
    dataset_choices.append("all")
    parser.add_argument(
        "--dataset",
        choices=dataset_choices,
        required=False,
        help=f"Select the dataset to preprocess.",
        default="all",
    )

    parser.set_defaults(func=main)

    return parser


class Preprocessor:
    def __init__(
        self,
        log_pattern: str,
        timestamp_format: Optional[str] = None,
        strict: bool = False,
    ):
        if timestamp_format and "<timestamp>" not in log_pattern.lower():
            raise ValueError(
                f"`Timestamp` field not in the given log format: `{log_pattern}`"
            )

        if "<content>" not in log_pattern.lower():
            raise ValueError(
                f"`Content` field not in the given log format: `{log_pattern}`"
            )

        self.log_pattern = re.compile(log_pattern)
        self.timestamp_format = timestamp_format
        self.strict = strict

    @staticmethod
    def __convert_to_iso8601(timestamp: str, format: str) -> str:
        try:
            dt = (
                datetime.fromtimestamp(float(timestamp))
                if format.lower() == "unix"
                else datetime.strptime(timestamp, format)
            )
            return dt.isoformat() + "Z"  # Append 'Z' to indicate UTC
        except ValueError as e:
            raise ValueError(
                f"Timestamp `{timestamp}` does not match format `{format}`: {e}"
            )

    def preprocess(self, raw_log: str) -> dict[str, str]:
        raw_log = raw_log.strip()
        matched = self.log_pattern.match(raw_log)

        if matched is None:
            if self.strict:
                raise ValueError(
                    f"Log `{raw_log}` can't be matched with pattern `{self.log_pattern}`."
                )
            return {"Content": raw_log}

        structured = matched.groupdict()

        if self.timestamp_format:
            structured["Timestamp"] = Preprocessor.__convert_to_iso8601(
                structured["Timestamp"],
                self.timestamp_format,
            )

        return structured


# Only this, first task (preprocessing), has dataset-specific inputs; this has been done to facilitate automatic
# downstream tasks. Basically, only this phase needs dataset-specific parameter tweaking, all downstream tasks
# need only algorithm parameter tweaking.
DATASET_PREPROCESSING_PARAMETERS = {
    "Apache": (
        join("data", "loghub_full", "Apache", "Apache_full.log"),
        r"\[(?P<Timestamp>.+?)\]\s+\[(?P<LogLevel>\w+)]\s+(?P<Content>.+)",
        "%a %b %d %H:%M:%S %Y",
    ),
    "BGL": (
        join("data", "loghub_full", "BGL", "BGL_full.log"),
        r"(?P<Label>(\w+|\-))\s+(?P<Timestamp>\d+)\s+(?P<Date>\d{4}\.\d{2}\.\d{2})\s+"
        r"(?P<Node>(\w|\d|\-|\:)+)\s+"
        r"(?P<Time>\d{4}\-\d{2}\-\d{2}\-\d{2}\.\d{2}\.\d{2}\.\d{6})\s+"
        r"(?P<NodeRepeated>(\w|\d|\-|\:)+)\s+"
        r"(?P<Type>\w+)\s+(?P<Component>\w+)\s+(?P<Level>\w+)\s+(?P<Content>.+)",
        "UNIX",
    ),
    "Hadoop": (
        join("data", "loghub_full", "Hadoop", "Hadoop_full.log"),
        r"(?P<Timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+"
        r"(?P<LogLevel>\w+)\s+"
        r"\[(?P<Thread>[^\]]+)\]\s+"
        r"(?P<Class>[\w\.\$]+):\s+"
        r"(?P<Content>.+)",
        "%Y-%m-%d %H:%M:%S,%f",
    ),
    "HDFS": (
        join("data", "loghub_full", "HDFS", "HDFS_full.log"),
        r"(?P<Timestamp>\d{6} \d{6})\s+"
        r"(?P<ThreadID>\d+)\s+"
        r"(?P<LogLevel>\w+)\s+"
        r"(?P<Class>[\w\.$]+):\s+"
        r"(?P<Content>.+)",
        "%y%m%d %H%M%S",
    ),
    "HealthApp": (
        join("data", "loghub_full", "HealthApp", "HealthApp_full.log"),
        r"(?P<Timestamp>\d+\-\d+\:\d+\:\d+\:\d+)\|"
        r"(?P<Component>[\w_]+)\|"
        r"(?P<ProcessID>\d+)\|"
        r"(?P<Content>.+)",
        "%Y%m%d-%H:%M:%S:%f",
    ),
    "HPC": (
        join("data", "loghub_full", "HPC", "HPC_full.log"),
        r"(?P<LogID>\d+)\s+"
        r"(?P<Node>(?:\w+(?:\s+\w+)*\s+)?[\w\d\-]+)\s+"
        r"(?P<Component>[\w\._\-]+)\s+"
        r"(?P<State>[\w\._\-]+)\s+"
        r"(?P<Timestamp>\d+)\s+"
        r"(?P<Flag>-?\d+)\s+"
        r"(?P<Content>.+)",
        "UNIX",
    ),
    "OpenStack": (
        join("data", "loghub_full", "OpenStack", "OpenStack_full.log"),
        r"(?P<LogFileName>\S+)\s+"
        r"(?P<Timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+"
        r"(?P<ProcessID>\d+)\s+"
        r"(?P<LogLevel>\w+)\s+"
        r"(?P<Component>[\w\.\-]+)\s+"
        r"\[(?P<RequestID>[\w\-\s]+)\]\s+"
        r"(?P<Content>.+)",
        "%Y-%m-%d %H:%M:%S.%f",
    ),
    "Spark": (
        join("data", "loghub_full", "Spark", "Spark_full.log"),
        r"(?P<Timestamp>\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\s+"
        r"(?P<LogLevel>\w+)\s+"
        r"(?P<Component>[\w\.$]+)\:\s+"
        r"(?P<Content>.+)",
        "%y/%m/%d %H:%M:%S",
    ),
    "Thunderbird": (
        join("data", "loghub_full", "Thunderbird", "Thunderbird_full.log"),
        r"\-\s+"
        r"(?P<Timestamp>\d+)\s+"
        r"(?P<Date>\d{4}\.\d{2}\.\d{2})\s+"
        r"(?P<User>[\w\d\-#]+)\s+"
        r"(?P<Month>\w{3})\s+"
        r"(?P<Day>\d{1,2})\s+"
        r"(?P<Time>\d{2}:\d{2}:\d{2})\s+"
        r"(?P<Location>[\S#]+(@|/)[\S#]+)\s+"
        r"(?P<Component>[\w\d/\.\-\(\)\s\<\>_]+)"
        r"(?:\[(?P<PID>\d+)\])?:\s+"
        r"(?P<Content>.+)",
        "UNIX",
    ),
    "Zookeeper": (
        join("data", "loghub_full", "Zookeeper", "Zookeeper_full.log"),
        r"(?P<Timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+\-\s+"
        r"(?P<LogLevel>\w+)\s+"
        r"\[(?P<NodeComponent>[^@]+)@"
        r"(?P<Id>\d+)]\s*-\s+"
        r"(?P<Content>.+)",
        "%Y-%m-%d %H:%M:%S,%f",
    ),
}


def main(args: Optional[argparse.Namespace] = None):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(METRICS_DIR, exist_ok=True)

    if not args:
        args = get_parser().parse_args()

    datasets_to_process = (
        DATASET_PREPROCESSING_PARAMETERS
        if args.dataset == "all"
        else {
            key: value
            for key, value in DATASET_PREPROCESSING_PARAMETERS.items()
            if key == args.dataset
        }
    )

    metrics_gathered = []

    for (
        logfile,
        log_pattern,
        timestamp_format,
    ) in datasets_to_process.values():
        preprocessor = Preprocessor(
            log_pattern,
            timestamp_format,
            strict=args.strict,
        )
        dataset_name = get_dataset_name(logfile)
        metrics_monitor = MetricsMonitor()

        log_count = 0
        unmatched_count = 0
        start = perf_counter()

        batch = []
        result_file = join(RESULTS_DIR, f"{dataset_name}.csv")
        with open(result_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = None

            metrics_monitor.start()
            for raw_log in log_generator(logfile):
                batch.append(preprocessor.preprocess(raw_log))

                if len(batch[-1].keys()) == 1:
                    unmatched_count += 1

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

            metrics_df = metrics_monitor.stop(log_count)
            metrics_df["Dataset"] = dataset_name
            metrics_df["Unmatched logs"] = round(unmatched_count * 100.0 / log_count, 4)

            metrics_gathered.append(metrics_df)

        end = perf_counter()
        logger.info(
            f"Dataset `{dataset_name}` finished preprocessing at an "
            f"average rate of {log_count/(end-start)} [log/sec] - {log_count} logs in {end-start} seconds. "
            f"Unmatched logs: {unmatched_count * 100. / log_count} [%]"
        )

    pd.concat(metrics_gathered, ignore_index=True).to_csv(
        join(METRICS_DIR, f"preprocessing_{datetime.now().isoformat()}.csv"),
        index=False,
    )


if __name__ == "__main__":
    main()
