import pandas as pd


def fixed_time_window(
    data: pd.DataFrame,
    timestamp_label: str,
    timestamp_format: str,
    window_size: str,
) -> pd.DataFrame:
    """
    Groups data into fixed-size time windows.

    Args:
        data (pd.DataFrame): Input DataFrame containing a timestamp column.
        timestamp_label (str): Name of the timestamp column.
        timestamp_format (str): Format of the timestamp (if not already datetime).
        window_size (str): Pandas time frequency string (e.g., '1Min', '30S', '5Min').

    Returns:
        pd.DataFrame: DataFrame grouped by fixed time windows.
    """
    if not pd.api.types.is_datetime64_any_dtype(data[timestamp_label]):
        data[timestamp_label] = pd.to_datetime(
            data[timestamp_label], format=timestamp_format
        )

    data["Window"] = data[timestamp_label].dt.floor(window_size)

    return data.groupby("Window").agg(list).reset_index()
