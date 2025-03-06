from os import makedirs, pardir
from os.path import dirname, exists, join, splitext

import pandas as pd

from ..util import get_all_files_recursively, get_dataset_name
from .pca import pca_subspace_anomaly_detection

RESULTS_DIR = join(dirname(__file__), "results")
INPUT_DIR = join(dirname(__file__), pardir, "features", "results")


def main():
    if not exists("results"):
        makedirs(join(RESULTS_DIR, "loghub_2k"), exist_ok=True)
        makedirs(join(RESULTS_DIR, "elfak"), exist_ok=True)

    for input_file in get_all_files_recursively(INPUT_DIR):
        dataset_name = get_dataset_name(input_file)
        input_file = join(INPUT_DIR, input_file)

        if not exists(input_file):
            raise ValueError(
                f"Event count matrix `{splitext(input_file)[-2]}` doesn't exist!"
            )

        event_count_matrix = pd.read_csv(input_file, index_col=0)

        pca_anomalies = pca_subspace_anomaly_detection(
            event_count_matrix,
            variance_threshold=0.85,
            alpha=0.05,
        )

        pca_anomalies.to_csv(join(RESULTS_DIR, f"{dataset_name}_pca.csv"))
        print(f"PCA anomaly detection executed for `{dataset_name}`")


if __name__ == "__main__":
    main()
