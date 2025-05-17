
from typing import Any, TYPE_CHECKING
import polars as pl
import pandas as pd
from polars._typing import PolarsDataType

from arkalos.utils.str_utils import snake, truncate



class DataTransformer:

    _df: pl.DataFrame

    def __init__(self, data: pl.DataFrame|pd.DataFrame|list[dict[str, Any]]):
        if not isinstance(data, pl.DataFrame):
            data = pl.DataFrame(data)
        self._df = data

    def renameColsSnakeCase(self) -> 'DataTransformer':
        self._df = self._df.rename(snake)
        return self
    
    def renameColsTruncateMaxLength(self, max_length: int) -> 'DataTransformer':
        self._df = self._df.rename(lambda col_name: truncate(col_name, max_length))
        return self
    
    def dropRowsByID(self, id: int|str) -> 'DataTransformer':
        self._df = self._df.remove(pl.col('id') == id)
        return self

    def dropRowsDuplicate(self) -> 'DataTransformer':
        self._df = self._df.unique()
        return self
    
    def dropRowsNullsAndNaNs(self) -> 'DataTransformer':
        self._df = self._df.drop_nans()
        self._df = self._df.drop_nulls()
        return self
    
    def dropCols(self, col_names: Any) -> 'DataTransformer':
        self._df = self._df.drop(col_names)
        return self

    def dropColsSameValueNoVariance(self) -> 'DataTransformer':
        constant_cols = [col for col in self._df.columns if self._df[col].n_unique() <= 1]
        self._df = self._df.drop(constant_cols)
        return self
    
    def splitColsOneHotEncode(self, col_names: Any|None = None) -> 'DataTransformer':
        if col_names is None:
            col_names = self._df.select(pl.col(pl.Enum)).columns
        self._df = self._df.to_dummies(col_names)
        return self
    
    def _getPolarsDataFrame(self, df: pl.DataFrame, frm: str|None = None, to: str|None = None) -> pl.DataFrame:
        cols = df.columns
        if frm is not None and to is not None:
            return df.select(cols[cols.index(frm):cols.index(to)+1])
        elif frm and to is None:
            start_index = cols.index(frm)
            return df.select(cols[start_index:])
        elif frm is None and to is not None:
            end_index = cols.index(to)
            return df.select(cols[:end_index + 1])
        else:
            return df
    
    def get(self, frm: str|None = None, to: str|None = None) -> pl.DataFrame:
        return self._getPolarsDataFrame(self._df, frm, to)
    
    def getNumeric(self, frm: str|None = None, to: str|None = None) -> pl.DataFrame:
        df = self._df.select(pl.col(pl.selectors.NUMERIC_DTYPES))
        return self._getPolarsDataFrame(df, frm, to)

    def getText(self, frm: str|None = None, to: str|None = None) -> pl.DataFrame:
        df = self._df.select(pl.selectors.string())
        return self._getPolarsDataFrame(df, frm, to)
