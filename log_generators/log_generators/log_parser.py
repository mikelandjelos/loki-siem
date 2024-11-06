import csv
import string
from json import dumps


def parse_logs(
    filename: str,
    encoding: str = "utf-8",
):
    with open(filename, mode="rt", encoding=encoding) as csv_file:
        attributes = [
            attr.strip(f'"{string.whitespace}')
            for attr in csv_file.readline().split(",")
        ]

        reader = csv.DictReader(
            csv_file,
            fieldnames=attributes,
            doublequote=True,
        )

        for row in reader:
            yield dumps(row)


__all__ = [
    "parse_logs",
]
