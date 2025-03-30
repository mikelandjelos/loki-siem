from os import makedirs, pardir
from os.path import dirname, exists, join

import pandas as pd

from ..utils.functions import get_all_files_recursively, get_dataset_name
from .plots import (
    plot_event_correlation,
    plot_event_heatmap,
    plot_histogram,
    plot_timeseries,
    plot_tsne,
)

RESULTS_DIR = join("results", "visualization")
INPUT_DIR = join("results", "anomalies")


def create_plots(anomaly_results_path, output_dir=None):
    """
    Visualizes PCA-based anomaly detection results.

    Args:
        anomaly_results_path (str): Path to the CSV file with anomaly detection results
        output_dir (str, optional): Directory to save visualization outputs

    Returns:
        dict: Dictionary containing anomaly statistics
    """
    anomaly_df = pd.read_csv(anomaly_results_path, index_col=0)

    # If index is not a datetime, try to convert it.
    try:
        anomaly_df.index = pd.to_datetime(anomaly_df.index)
        time_based_index = True
    except:
        time_based_index = False

    anomaly_scores = anomaly_df["AnomalyScore"]
    is_anomaly = anomaly_df["IsAnomaly"]

    event_count_matrix = anomaly_df.drop(["AnomalyScore", "IsAnomaly"], axis=1)

    if output_dir and not exists(output_dir):
        makedirs(output_dir, exist_ok=True)

    plot_timeseries(
        anomaly_df,
        time_based_index,
        join(output_dir, "anomaly_scores_timeseries.png") if output_dir else None,
    )

    plot_histogram(
        anomaly_scores,
        join(output_dir, "anomaly_scores_histogram.png") if output_dir else None,
    )

    plot_event_heatmap(
        event_count_matrix,
        time_based_index,
        join(output_dir, "event_heatmap.png") if output_dir else None,
    )

    # t-SNE visualization if we have enough data points.
    if len(event_count_matrix) > 10:
        plot_tsne(
            event_count_matrix,
            anomaly_scores,
            is_anomaly,
            join(output_dir, "tsne_visualization.png") if output_dir else None,
        )

    plot_event_correlation(
        event_count_matrix,
        anomaly_scores,
        join(output_dir, "event_correlation.png") if output_dir else None,
    )


def main():
    for input_file in get_all_files_recursively(INPUT_DIR):
        dataset_name = get_dataset_name(input_file)
        input_file = join(INPUT_DIR, dataset_name, f"{dataset_name}.csv")

        if not exists(input_file):
            print(f"Anomaly detection results not found at: `{input_file}`")
            continue

        dataset_result_dir = join(RESULTS_DIR, dataset_name)
        makedirs(dataset_result_dir, exist_ok=True)

        create_plots(input_file, dataset_result_dir)


if __name__ == "__main__":
    main()
