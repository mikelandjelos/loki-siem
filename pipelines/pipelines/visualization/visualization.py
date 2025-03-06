from os import makedirs, pardir
from os.path import dirname, exists, join

import pandas as pd

from ..util import get_all_files_recursively, get_dataset_name
from .plots import (
    plot_event_correlation,
    plot_event_heatmap,
    plot_histogram,
    plot_timeseries,
    plot_tsne,
)

RESULTS_DIR = join(dirname(__file__), "results")
INPUT_DIR = join(dirname(__file__), pardir, "anomalies", "results")


def calculate_statistics(anomaly_df: pd.DataFrame) -> dict[str, int | float]:
    """
    Calculate anomaly statistics.

    Args:
        anomaly_df (pd.DataFrame): DataFrame with anomaly scores and labels

    Returns:
        dict: Dictionary containing anomaly statistics
    """
    anomaly_scores = anomaly_df["AnomalyScore"]
    is_anomaly = anomaly_df["IsAnomaly"]

    return {
        "total_windows": len(anomaly_df),
        "anomaly_count": is_anomaly.sum(),
        "anomaly_percentage": is_anomaly.mean() * 100,
        "max_anomaly_score": anomaly_scores.max(),
        "avg_anomaly_score": anomaly_scores.mean(),
    }


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

    threshold = (
        anomaly_df.loc[anomaly_df["IsAnomaly"].idxmax(), "AnomalyScore"]
        if any(is_anomaly)
        else anomaly_scores.max()
    )

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
        threshold,
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
    """
    Main function to visualize anomaly detection results.
    """

    if not exists(RESULTS_DIR):
        makedirs(RESULTS_DIR, exist_ok=True)

    for dataset_path in get_all_files_recursively(INPUT_DIR):
        if not exists(dataset_path):
            print(f"Anomaly results not found at: `{dataset_path}`")
            continue

        dataset_name = get_dataset_name(dataset_path)
        dataset_visualization_dir = join(RESULTS_DIR, dataset_name)

        if not exists(dataset_visualization_dir):
            makedirs(dataset_visualization_dir, exist_ok=True)

        print(f"Visualizing anomaly detection results for {dataset_name}...")
        stats = create_plots(dataset_path, dataset_visualization_dir)
        print(f"Anomaly Statistics: {stats}")


if __name__ == "__main__":
    main()
