import json
import os

import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA


def load_clustered_logs(results_path: str) -> pd.DataFrame:
    data = []
    for file_name in os.listdir(results_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(results_path, file_name)
            with open(file_path, "r") as file:
                batch_data = json.load(file)
                data.extend(batch_data)
    return pd.DataFrame(data)


def generate_html_report(df: pd.DataFrame, output_path: str):
    cluster_counts = df["cluster"].value_counts()
    cluster_fig = px.bar(
        cluster_counts,
        x=cluster_counts.index,
        y=cluster_counts.values,
        labels={"x": "Cluster", "y": "Number of Logs"},
        title="Cluster Distribution",
    )

    features = pd.DataFrame(df["feature_vector"].tolist())
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(features)
    feature_fig = px.scatter(
        x=reduced_features[:, 0],
        y=reduced_features[:, 1],
        color=df["cluster"],
        labels={"x": "PC1", "y": "PC2", "color": "Cluster"},
        title="Feature Vectors (PCA Reduced)",
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    timeline = df.set_index("timestamp").resample("1min").size()
    timeline_fig = px.line(
        timeline,
        labels={"value": "Number of Logs", "timestamp": "Time"},
        title="Log Timeline",
    )

    with open(output_path, "w") as f:
        f.write("<html><head><title>Log Analysis Report</title></head><body>")
        f.write(cluster_fig.to_html(full_html=False, include_plotlyjs="cdn"))
        f.write(feature_fig.to_html(full_html=False, include_plotlyjs="cdn"))
        f.write(timeline_fig.to_html(full_html=False, include_plotlyjs="cdn"))
        f.write("</body></html>")


def main():
    RESULTS_PATH = "results"

    for analysis in os.listdir(RESULTS_PATH):
        analysis_path = os.path.join(RESULTS_PATH, analysis)
        if not os.path.exists(analysis_path):
            print(f"Analysis path '{analysis_path}' does not exist.")
            return

        df = load_clustered_logs(analysis_path)

        if df.empty:
            print("No data to visualize.")
            return

        report_path = os.path.join(analysis_path, "report.html")
        generate_html_report(df, report_path)
        print(f"Report saved to {report_path}")


if __name__ == "__main__":
    main()
