from os.path import exists, join

import pandas as pd

from ..utils.functions import (
    dataset_to_csv,
    get_all_files_recursively,
    get_dataset_name,
)
from .event_count_matrix import event_count_matrix
from .windowing import fixed_time_window

RESULTS_DIR = join("results", "features")
INPUT_DIR = join("results", "parsing")
INPUT_FILES: list[tuple[str, str, str]] = [
    ("drain/loghub_2k/Apache_2k_structured.csv", "Time", r"%a %b %d %H:%M:%S %Y"),
    # ("drain3/", "Time", r"%a %b %d %H:%M:%S %Y"),
]  # TODO: This shouldn't exist, should be replaced with get_all_files_recursively(INPUT_DIR) - ISO8601 Timestamp!


def main():
    for input_file, timestamp_label, timestamp_format in INPUT_FILES:
        dataset_name = get_dataset_name(input_file)
        input_file = join(
            INPUT_DIR, input_file
        )  # TODO: Should be changed after the TODO above is done.

        if not exists(input_file):
            raise ValueError(f"Structured log file `{input_file}` doesn't exist!")

        df = pd.read_csv(input_file)

        fixed_window_df = fixed_time_window(
            df,
            timestamp_label,
            timestamp_format,
            window_size="5min",
        )

        # TODO: Add sliding and session windows.
        ecm_fixed_window = event_count_matrix(fixed_window_df)
        dataset_name = f"{dataset_name}_ecmfixed"
        dataset_to_csv(ecm_fixed_window, RESULTS_DIR, dataset_name)

        print(f"Features created for `{dataset_name}`")


if __name__ == "__main__":
    main()
