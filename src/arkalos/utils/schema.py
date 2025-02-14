import re
import polars as pl
import json

DATE_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
    r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
    r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z',  # ISO 8601 (e.g., 2025-01-15T12:34:56.000Z)
]

def is_date_column(column: pl.Series, threshold: float = 0.8) -> bool:
    """
    Check if a column contains date-like values.
    Args:
        column: Polars Series to check.
        threshold: Minimum fraction of values that must match a date pattern.
    Returns:
        bool: True if the column is likely a date column.
    """
    match_count = 0
    for value in column:
        if value is None:
            continue
        for pattern in DATE_PATTERNS:
            if re.fullmatch(pattern, str(value)):
                match_count += 1
                break
    # Check if the match rate exceeds the threshold
    return (match_count / len(column)) >= threshold

def detect_date_columns(df: pl.DataFrame, threshold: float = 0.8) -> list:
    """
    Detect date columns in a DataFrame.
    Args:
        df: Polars DataFrame to analyze.
        threshold: Minimum fraction of values that must match a date pattern.
    Returns:
        list: Names of columns detected as date columns.
    """
    date_columns = []
    for column in df.columns:
        if is_date_column(df[column], threshold):
            date_columns.append(column)
    return date_columns

def parse_date_columns(df: pl.DataFrame, date_columns: list) -> pl.DataFrame:
    """
    Parse detected date columns into datetime type.
    Args:
        df: Polars DataFrame.
        date_columns: List of column names to parse as dates.
    Returns:
        pl.DataFrame: DataFrame with parsed date columns.
    """
    for column in date_columns:
        df = df.with_columns(pl.col(column).str.strptime(pl.Datetime))
    return df

def get_data_schema(data) -> pl.Schema:
    df = pl.DataFrame(data[:10])
    date_columns = detect_date_columns(df)
    df = parse_date_columns(df, date_columns)
    return df.schema
