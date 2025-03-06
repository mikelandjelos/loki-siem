import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.manifold import TSNE


def plot_timeseries(anomaly_df, time_based_index, output_path=None):
    """
    Plot time series of anomaly scores with anomalies highlighted.

    Args:
        anomaly_df (pd.DataFrame): DataFrame with anomaly scores and labels
        time_based_index (bool): Whether the index is time-based
        output_path (str, optional): Path to save the visualization
    """
    anomaly_scores = anomaly_df["AnomalyScore"]
    is_anomaly = anomaly_df["IsAnomaly"]

    plt.figure(figsize=(12, 5))
    plt.plot(anomaly_scores, color="blue", alpha=0.7, label="Anomaly Score")

    # Highlight anomalies.
    anomaly_points = anomaly_df[is_anomaly].index
    plt.scatter(
        anomaly_points,
        anomaly_df.loc[anomaly_points, "AnomalyScore"],
        color="red",
        s=50,
        label="Anomaly",
    )

    # Add threshold line.
    threshold = (
        anomaly_df.loc[anomaly_df["IsAnomaly"].idxmax(), "AnomalyScore"]
        if any(is_anomaly)
        else anomaly_scores.max()
    )
    plt.axhline(y=threshold, color="r", linestyle="--", alpha=0.5, label="Threshold")

    plt.title("Anomaly Scores Over Time")
    plt.xlabel("Time Window" if time_based_index else "Window Index")
    plt.ylabel("Anomaly Score (SPE)")
    plt.legend()

    if time_based_index:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.gcf().autofmt_xdate()

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_histogram(anomaly_scores, threshold, output_path=None):
    """
    Plot histogram of anomaly scores with threshold line.

    Args:
        anomaly_scores (pd.Series): Series of anomaly scores
        threshold (float): Anomaly threshold value
        output_path (str, optional): Path to save the visualization
    """
    plt.figure(figsize=(10, 5))
    sns.histplot(anomaly_scores, bins=30, kde=True)
    plt.axvline(x=threshold, color="r", linestyle="--", label="Threshold")

    plt.title("Distribution of Anomaly Scores")
    plt.xlabel("Anomaly Score (SPE)")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_event_heatmap(event_count_matrix, time_based_index, output_path=None):
    """
    Plot heatmap of top events by variance.

    Args:
        event_count_matrix (pd.DataFrame): Matrix of event counts
        time_based_index (bool): Whether the index is time-based
        output_path (str, optional): Path to save the visualization
    """
    # Get top 20 events by variance.
    top_events = (
        event_count_matrix.var().sort_values(ascending=False).head(20).index.tolist()
    )

    plt.figure(figsize=(14, 8))
    sns.heatmap(
        event_count_matrix[top_events].T,
        cmap="YlGnBu",
        xticklabels=50 if len(event_count_matrix) > 50 else True,
    )

    plt.title("Event Frequency Heatmap (Top Events by Variance)")
    plt.xlabel("Time Window" if time_based_index else "Window Index")
    plt.ylabel("Event Template")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_tsne(event_count_matrix, anomaly_scores, is_anomaly, output_path=None):
    """
    Plot t-SNE visualization of event count matrix.

    Args:
        event_count_matrix (pd.DataFrame): Matrix of event counts
        anomaly_scores (pd.Series): Series of anomaly scores
        is_anomaly (pd.Series): Boolean series indicating anomalies
        output_path (str, optional): Path to save the visualization
    """
    # Apply t-SNE to visualize high-dimensional data in 2D.
    tsne = TSNE(n_components=2, random_state=42)
    tsne_results = tsne.fit_transform(event_count_matrix)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        tsne_results[:, 0],
        tsne_results[:, 1],
        c=anomaly_scores,
        cmap="coolwarm",
        alpha=0.7,
    )

    # Mark anomalies with a different marker.
    if any(is_anomaly):
        anomaly_indices = np.where(is_anomaly)[0]
        plt.scatter(
            tsne_results[anomaly_indices, 0],
            tsne_results[anomaly_indices, 1],
            color="red",
            marker="*",
            s=150,
            label="Anomaly",
            edgecolors="black",
        )

    plt.colorbar(scatter, label="Anomaly Score")
    plt.title("t-SNE Visualization of Event Count Matrix")
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    plt.legend()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    plt.close()


def plot_event_correlation(event_count_matrix, anomaly_scores, output_path=None):
    """
    Plot correlation between anomaly scores and event counts.

    Args:
        event_count_matrix (pd.DataFrame): Matrix of event counts
        anomaly_scores (pd.Series): Series of anomaly scores
        output_path (str, optional): Path to save the visualization
    """
    # Calculate correlation between anomaly scores and event counts.
    corr = pd.DataFrame({"correlation": event_count_matrix.corrwith(anomaly_scores)})
    corr = corr.sort_values("correlation", ascending=False)

    # Plot the top 10 most correlated events.
    plt.figure(figsize=(12, 6))
    top_corr = corr.head(10)
    top_corr["correlation"].plot(kind="bar")

    plt.title("Top 10 Events Most Correlated with Anomaly Scores")
    plt.xlabel("Event Template")
    plt.ylabel("Correlation Coefficient")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    plt.close()
