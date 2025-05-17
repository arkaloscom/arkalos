
from typing import Type, Any, get_type_hints
from enum import Enum
from dataclasses import fields as dc_fields, is_dataclass
import re
import json
import polars as pl
from pydantic import BaseModel
from polars.datatypes import DataTypeClass, DataType
from datetime import datetime

from arkalos.utils.str_utils import snake



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





def _map_python_type_to_polars(typ: Any) -> DataTypeClass|DataType:
    if typ == str:
        return pl.Utf8
    elif typ == int:
        return pl.Int64
    elif typ == float:
        return pl.Float64
    elif typ == bool:
        return pl.Int8 # use int for bollean
    elif typ == datetime:
        return pl.Datetime
    elif isinstance(typ, type) and issubclass(typ, Enum):
        return pl.Enum(typ)
    else:
        raise ValueError(f'Unsupported type {typ} for Polars schema.')

def _dataclass_to_polars_schema(dc_cls: Type[Any]) -> dict[str, DataTypeClass|DataType]:
    if not hasattr(dc_cls, '__dataclass_fields__'):
        raise ValueError('Input must be a dataclass class.')
    
    schema = {}
    for field in dc_fields(dc_cls):
        schema[field.name] = _map_python_type_to_polars(field.type)
    return schema

def _pydantic_model_to_polars_schema(model_cls: Type[BaseModel]) -> dict[str, DataTypeClass|DataType]:
    if not issubclass(model_cls, BaseModel):
        raise ValueError('Input must be a Pydantic model class.')
    
    schema = {}
    for name, field in model_cls.model_fields.items():
        typ = field.annotation
        schema[name] = _map_python_type_to_polars(typ)
    return schema

def to_polars_schema(cls: Type[BaseModel]|Type[Any]) -> dict[str, DataTypeClass|DataType]:
    if issubclass(cls, BaseModel):
        return _pydantic_model_to_polars_schema(cls)
    elif hasattr(cls, '__dataclass_fields__'):
        return _dataclass_to_polars_schema(cls)
    else:
        raise ValueError('Unsupported class type. Expected a Pydantic model or a dataclass.')
    