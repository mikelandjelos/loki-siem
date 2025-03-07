from os import makedirs, pardir
from os.path import exists, join

import pandas as pd

from ..util import dataset_to_csv, get_all_files_recursively, get_dataset_name
from .pca import pca_subspace_anomaly_detection

RESULTS_DIR = join("results", "anomalies")
INPUT_DIR = join("results", "features")


def main():
    for input_file in get_all_files_recursively(INPUT_DIR):
        dataset_name = get_dataset_name(input_file)
        input_file = join(INPUT_DIR, dataset_name, f"{dataset_name}.csv")

        if not exists(input_file):
            raise ValueError(f"Event count matrix `{input_file}` doesn't exist!")

        event_count_matrix = pd.read_csv(input_file, index_col=0)

        pca_anomalies_df = pca_subspace_anomaly_detection(
            event_count_matrix,
            variance_threshold=0.9,
            alpha=0.001,
        )
        dataset_name = f"{dataset_name}_pca"
        dataset_to_csv(pca_anomalies_df, RESULTS_DIR, dataset_name)

        print(f"Anomalies detection executed for `{dataset_name}`")


if __name__ == "__main__":
    main()
