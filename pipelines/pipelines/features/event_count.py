import pandas as pd


def event_count_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an event count matrix based on EventTemplate occurrences per window.
    Windows can be created using different strategies:
        - Fixed time window;
        - Sliding time window;
        - Session (ID-based) window.

    Args:
        data (pd.DataFrame): Input DataFrame with columns 'Window' and 'EventTemplate'.

    Returns:
        pd.DataFrame: Event count matrix (rows = time windows, columns = event templates).
    """
    if "EventTemplate" not in data.columns:
        raise ValueError("The input DataFrame must contain an 'EventTemplate' column.")

    data = data.explode("EventTemplate")

    event_count_df = (
        data.groupby(["Window", "EventTemplate"])
        .size()
        .unstack(fill_value=0)  # Convert grouped counts into a pivot table
    )

    return event_count_df
