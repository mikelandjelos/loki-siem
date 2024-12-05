import csv
import json
import string
import time
from datetime import datetime, timezone
from typing import Any, Optional

from dateutil.parser import parse
from tomli import load

from .types import GlobalConfig
from .util import reversed_lines


def logfile_to_logstream(
    filename: str,
    timestamp_label: str = "timestamp",
    timestamp_format: str = "iso8601",
    encoding: str = "utf-8",
    reverse_order: bool = False,
):
    with open(
        filename,
        mode="rt",
        encoding=encoding,
    ) as csv_file:
        attributes = [
            attr.strip(f'"{string.whitespace}')
            for attr in csv_file.readline().split(",")
        ]

        reader = csv.DictReader(
            reversed_lines(csv_file) if reverse_order else csv_file,
            fieldnames=attributes,
        )

        old_timestamp: datetime | None = None

        for row in reader:
            new_timestamp: str | datetime | None = row.get(timestamp_label, None)

            assert (
                new_timestamp is not None
            ), f"Log `{row}` doesn't have a timestamp data labeled `{timestamp_label}`"
            assert isinstance(
                new_timestamp, str
            ), f"`{new_timestamp}` is of type `{type(new_timestamp)}`, but should be `str`"

            new_timestamp = (
                parse(new_timestamp)
                if timestamp_format.lower() == "iso8601"
                else datetime.strptime(new_timestamp, timestamp_format)
            )

            sleep_duration = (
                (new_timestamp - old_timestamp).total_seconds()
                if old_timestamp is not None
                else 0.0
            )

            time.sleep(sleep_duration)
            row[timestamp_label] = datetime.now(timezone.utc).isoformat()
            yield json.dumps(row)

            old_timestamp = new_timestamp


def parse_toml_config(file_path: str) -> GlobalConfig:
    generators_config: GlobalConfig

    with open(file_path, "rb") as toml_file:
        config: Optional[dict[str, Any]] = load(toml_file)
        generators_config = GlobalConfig(**config)

    return generators_config
