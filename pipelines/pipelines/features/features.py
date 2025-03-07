from os import makedirs, pardir
from os.path import dirname, exists, join, splitext

import pandas as pd

from ..util import get_all_files_recursively, get_dataset_name
from .event_count import event_count_matrix
from .windowing import fixed_time_window

RESULTS_DIR = join(dirname(__file__), "results")
INPUT_DIR = join(dirname(__file__), pardir, "parsing", "drain", "results")
LOGHUB2K_INPUT_FILES: list[tuple[str, str, str]] = [
    ("loghub_2k/Apache_2k_structured.csv", "Time", r"%a %b %d %H:%M:%S %Y"),
]  # TODO: This shouldn't exist, should be replaced with get_all_files_recursively(INPUT_DIR) - ISO8601 Timestamp!


def main():
    if not exists("results"):
        makedirs(RESULTS_DIR, exist_ok=True)

    for input_file, timestamp_label, timestamp_format in LOGHUB2K_INPUT_FILES:
        dataset_name = get_dataset_name(input_file)
        input_file = join(INPUT_DIR, input_file)

        if not exists(input_file):
            raise ValueError(f"Log file `{input_file}` doesn't exist!")

        df = pd.read_csv(input_file)

        fixed_window_df = fixed_time_window(
            df,
            timestamp_label,
            timestamp_format,
            window_size="5min",
        )

        makedirs(join(RESULTS_DIR, dataset_name), exist_ok=True)
        event_count_matrix(fixed_window_df).to_csv(
            join(RESULTS_DIR, dataset_name, f"{dataset_name}_ecmfixed.csv")
        )

        # TODO: Add sliding and session windows.

        print(f"Features created for `{dataset_name}`")


if __name__ == "__main__":
    main()
