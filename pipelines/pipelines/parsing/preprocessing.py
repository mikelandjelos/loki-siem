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

    parser.set_defaults(func=main)

    return parser


class Preprocessor:
    def __init__(self, log_pattern: str, timestamp_format: str):
        if "Timestamp" not in log_pattern:
            raise ValueError(
                f"`Timestamp` field not in the given log format: `{log_pattern}`"
            )

        if "Content" not in log_pattern:
            raise ValueError(
                f"`Content` field not in the given log format: `{log_pattern}`"
            )

        self.log_pattern = re.compile(log_pattern)
        self.timestamp_format = timestamp_format

    def __convert_to_iso8601(self, timestamp: str) -> str:
        try:
            dt = datetime.strptime(timestamp, self.timestamp_format)
            return dt.isoformat() + "Z"  # Append 'Z' to indicate UTC
        except ValueError as e:
            raise ValueError(
                f"Timestamp `{timestamp}` does not match format `{self.timestamp_format}`: {e}"
            )

    def preprocess(self, raw_log: str) -> dict[str, str]:
        matched = self.log_pattern.match(raw_log)

        if not matched:
            raise ValueError(
                f"Log `{raw_log}` can't be matched with pattern `{self.log_pattern.pattern}`"
            )

        structured = matched.groupdict()
        structured["Timestamp"] = self.__convert_to_iso8601(structured["Timestamp"])

        return structured


DATASET_PREPROCESSING_PARAMETERS = {
    "Apache": (
        join("data", "loghub_full", "Apache", "Apache_full.log"),
        r"\[(?P<Timestamp>.+?)\]\s+\[(?P<LogLevel>\w+)]\s+(?P<Content>.+)",
        "%a %b %d %H:%M:%S %Y",
    ),
}


def main(args: Optional[argparse.Namespace] = None):
    if not exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)

    if not args:
        args = get_parser().parse_args()

    for (
        logfile,
        log_pattern,
        timestamp_format,
    ) in DATASET_PREPROCESSING_PARAMETERS.values():
        preprocessor = Preprocessor(log_pattern, timestamp_format)
        dataset_name = get_dataset_name(logfile)

        preprocessed_logs = []
        log_count = 0
        start = perf_counter()
        for raw_log in log_generator(logfile):
            preprocessed_logs.append(preprocessor.preprocess(raw_log))
            log_count += 1
        end = perf_counter()

        logger.info(
            f"Dataset `{dataset_name}` finished preprocessing at an "
            + f"average rate of {log_count/(end-start)} [log/sec]"
        )

        result_file = join(RESULTS_DIR, f"{dataset_name}.csv")
        with open(result_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = list(preprocessed_logs[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(preprocessed_logs)


if __name__ == "__main__":
    main()
