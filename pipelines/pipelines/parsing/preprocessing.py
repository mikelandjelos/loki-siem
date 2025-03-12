import argparse
import csv
import logging
import os
import re
import sys
from datetime import datetime, timezone
from os.path import exists, join
from time import perf_counter
from typing import Optional

from .._util import get_dataset_name, log_generator

RESULTS_DIR = join("results", "parsing", "preprocessing")

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
        help=f"Select the dataset to preprocess (options: \n{', '.join(DATASET_PREPROCESSING_PARAMETERS.keys())})",
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
    if not exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)

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

        log_count = 0
        unmatched_count = 0
        start = perf_counter()

        BATCH_SIZE = 10000
        preprocessed_logs = []
        result_file = join(RESULTS_DIR, f"{dataset_name}.csv")
        with open(result_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = None

            for raw_log in log_generator(logfile):
                preprocessed_logs.append(preprocessor.preprocess(raw_log))

                if len(preprocessed_logs[-1].keys()) == 1:
                    unmatched_count += 1

                if writer is None:
                    fieldnames = list(preprocessed_logs[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()

                log_count += 1

                if log_count % BATCH_SIZE == 0:
                    writer.writerows(preprocessed_logs)
                    preprocessed_logs = []

            if len(preprocessed_logs) > 0 and writer is not None:
                writer.writerows(preprocessed_logs)

        end = perf_counter()
        logger.info(
            f"Dataset `{dataset_name}` finished preprocessing at an "
            f"average rate of {log_count/(end-start)} [log/sec] - {log_count} logs in {end-start} seconds. "
            f"Unmatched logs: {unmatched_count * 100. / log_count} %"
        )


if __name__ == "__main__":
    main()
