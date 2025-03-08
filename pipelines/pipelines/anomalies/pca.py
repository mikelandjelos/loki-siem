import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import StandardScaler


def pca_subspace_anomaly_detection(
    event_matrix: pd.DataFrame, variance_threshold: float = 0.95, alpha: float = 0.001
):
    """
    Applies PCA-based subspace anomaly detection on the event count matrix.

    Implementation goes along with the papers:
     1. [Experience Report: System Log Analysis for Anomaly Detection](https://jiemingzhu.github.io/pub/slhe_issre2016.pdf);
     2. [Large-Scale System Problems Detection by Mining Console Logs](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2009/EECS-2009-103.pdf).

    Args:
        event_matrix (pd.DataFrame): The event count matrix (rows = time windows, columns = event templates).
        variance_threshold (float): The percentage of variance to preserve (default 95%).
        alpha (float): The significance level for anomaly detection (default 0.001).

    Returns:
        pd.DataFrame: Original event matrix with an additional 'AnomalyScore' column.
    """
    # Ensure the index ('Window' column) is not included in PCA.
    event_count_matrix = event_matrix.values

    # TF-IDF preprocessing - reasoning:
    #   => common events that appear in most time windows will have less influence.
    tfidf_transformer = TfidfTransformer(
        norm="l2",
        use_idf=True,
        smooth_idf=True,
    )
    event_count_matrix = tfidf_transformer.fit_transform(
        event_count_matrix
    ).toarray()  # type: ignore

    # Standardize the data (zero mean, unit variance) - not the same as normalization!
    scaler = StandardScaler()
    event_counts_scaled = scaler.fit_transform(event_count_matrix)

    # Apply PCA to find principal components capturing `variance_threshold` variance.
    pca = PCA(n_components=variance_threshold)
    principal_components = pca.fit(event_counts_scaled)
    k = principal_components.n_components_  # Number of selected principal components

    # Compute normal space (Sn) and anomaly space (Sa).

    # Principal component matrix (P = [v1, v2, ..., vk]).
    P = principal_components.components_.T

    # Identity matrix of original space
    I = np.identity(event_counts_scaled.shape[1])

    # Projection matrix to Sa.
    projection_matrix = I - P @ P.T

    # Compute projection onto anomaly space.
    projections = (projection_matrix @ event_counts_scaled.T).T  # ya = (I - P P^T) y
    squared_prediction_error = np.linalg.norm(projections, axis=1) ** 2  # SPE = ‖ya‖^2

    # Compute threshold Q_alpha using chi-squared distribution.
    # Q_alpha from chi-square.
    Q_alpha = chi2.ppf(1 - alpha, df=event_counts_scaled.shape[1] - k)

    # Label anomalies.
    event_matrix["AnomalyScore"] = squared_prediction_error
    event_matrix["IsAnomaly"] = event_matrix["AnomalyScore"] > Q_alpha

    return event_matrix
