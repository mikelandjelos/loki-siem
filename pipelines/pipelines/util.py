import os
from os.path import join

import pandas as pd


def get_all_files_recursively(directory: str) -> list[str]:
    """Recursively returns a list of all files in the given directory."""
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


def get_dataset_name(filepath: str) -> str:
    return os.path.splitext(os.path.basename(filepath))[0]


def dataset_to_csv(df: pd.DataFrame, results_dir, dataset_name: str):
    features_results_dir = join(results_dir, dataset_name)
    os.makedirs(features_results_dir, exist_ok=True)
    df.to_csv(join(features_results_dir, f"{dataset_name}.csv"))
