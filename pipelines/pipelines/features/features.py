from os import makedirs
from os.path import exists, join

import pandas as pd

from .windowing import fixed_time_window

RESULTS_BASE_PATH = "results/features/"
BASE_PATH = "results/drain"

DATA_PATHS: list[tuple[str, str, str]] = [
    ("loghub_2k/Apache_2k.log_structured.csv", "Time", r"%a %b %d %H:%M:%S %Y"),
]


def main():
    if not exists("results"):
        makedirs(join(RESULTS_BASE_PATH, "windowing"), exist_ok=True)

    for path, timestamp_label, timestamp_format in DATA_PATHS:
        path_with_base = join(BASE_PATH, path)

        if not exists(path_with_base):
            raise ValueError(f"Log file `{path_with_base}` doesn't exist!")

        df = pd.read_csv(path_with_base)
        fixed_time_window(df, timestamp_label, timestamp_format, "30min")


if __name__ == "__main__":
    main()
