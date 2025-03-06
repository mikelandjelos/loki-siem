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
]  # This shouldn't exist, should be replaced with get_all_files_recursively(INPUT_DIR)


def main():
    if not exists("results"):
        makedirs(join(RESULTS_DIR, "loghub_2k"), exist_ok=True)
        makedirs(join(RESULTS_DIR, "elfak"), exist_ok=True)

    for input_file, timestamp_label, timestamp_format in LOGHUB2K_INPUT_FILES:
        dataset_name = get_dataset_name(input_file)
        out_datafile = join(RESULTS_DIR, input_file.replace(".csv", "_ecm.csv"))
        input_file = join(INPUT_DIR, input_file)

        if not exists(input_file):
            raise ValueError(f"Log file `{input_file}` doesn't exist!")

        df = pd.read_csv(input_file)

        fixed_window_dfs = fixed_time_window(
            df,
            timestamp_label,
            timestamp_format,
            window_size="5min",
        )

        event_count_matrix(fixed_window_dfs).to_csv(
            out_datafile.replace("_ecm", "_ecmwfixed")
        )

        # TODO: Add sliding and session windows.

        print(f"Features created for `{dataset_name}`")


if __name__ == "__main__":
    main()
