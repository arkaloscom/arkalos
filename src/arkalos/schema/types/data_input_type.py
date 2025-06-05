
from __future__ import annotations
from typing import TYPE_CHECKING, Type, get_args
if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from dataclasses import dataclass, is_dataclass, asdict

from pydantic import BaseModel
import polars as pl
import pandas as pd



type DataItemType = DataclassInstance|BaseModel|dict
type DataItemClassType = Type[DataclassInstance]|Type[BaseModel]|Type[dict]
type DataCollectionType = pl.DataFrame|pd.DataFrame|list[DataclassInstance]|list[BaseModel]|list[dict]
type DataInputType = DataItemType|DataCollectionType



def input_item_to_dict(item: DataInputType) -> dict:
    if is_dataclass(item):
        return asdict(item)
    elif isinstance(item, BaseModel):
        return item.model_dump()
    elif isinstance(item, dict):
        return item
    else:
        raise ValueError(f'Unsupported data type: {type(item)}. \
                            Expected dataclass, Pydantic model, or dict.')



def input_to_df(data: DataInputType) -> pl.DataFrame:
    if isinstance(data, (pd.DataFrame, pl.DataFrame)):
        if isinstance(data, pd.DataFrame):
            return pl.from_pandas(data)
        return data
    elif isinstance(data, list):
        return pl.DataFrame([input_item_to_dict(item) for item in data])
    else:
        return pl.DataFrame([input_item_to_dict(data)])
    


def input_or_first_row_to_dict(data: DataInputType) -> dict:
    df = input_to_df(data)
    return df.to_dicts()[0]



def input_or_first_row_to_class(data: DataInputType, cls: DataItemClassType) -> DataItemType:
    return cls(**input_or_first_row_to_dict(data))
