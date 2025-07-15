def drop_empty_columns(df):
    """
    Remove columns that contain only NA values.

    Args:
        df (pd.DataFrame): DataFrame to be processed.

    Returns:
        pd.DataFrame: DataFrame with empty columns removed.
    """
    return df.dropna(axis='columns', how='all')
