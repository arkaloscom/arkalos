
from typing import get_args

import polars as pl

import sqlglot.expressions as exp

from arkalos.utils.str_utils import snake

from arkalos.schema.base_query_builder import BaseQueryBuilder
from arkalos.schema.dml.column_setter_builder import ColumnSetterBuilder
from arkalos.schema.types.data_input_type import DataItemType, DataCollectionType, DataInputType, input_to_df



class InsertQueryBuilder(BaseQueryBuilder):

    _tableName: str
    _tableGroup: str|None
    _col: str|None
    _val: str|int|None
    _df: pl.DataFrame|None

    def __init__(self, table_name: str, table_group: str|None = None):
        self._tableName = table_name
        self._tableGroup = table_group
        self._col = None
        self._val = None
        self._df = None

    def insert(self, item: DataItemType) -> 'InsertQueryBuilder':
        self._df = input_to_df(item)
        return self

    def insertMultiple(self, data: DataCollectionType) -> 'InsertQueryBuilder':
        self._df = input_to_df(data)
        return self

    def _buildColNames(self, df: pl.DataFrame) -> list[exp.Identifier]:
        cols = []
        for col_name in df.schema:
            cols.append(exp.Identifier(this=snake(col_name), quoted=False))
        return cols
    
    def _buildValues(self, df: pl.DataFrame) -> exp.Values:
        exps = []

        for row in df.iter_rows():
            exps.append(self._buildSingleValueRow(row))

        return exp.Values(
            expressions=exps
        )

    def _buildSingleValueRow(self, row: tuple) -> exp.Tuple:
        exps = []
        for value in row:
            exps.append(self._expFromDataType(value))

        return exp.Tuple(
            expressions=exps
        )

    def getExpression(self) -> exp.Insert:
        if self._df is None:
            raise TypeError('InsertQueryBuilder.getExpression(): use insert() first.')
        return exp.Insert(
            this=exp.Schema(
                this=self.tableNameExpression(self._tableName, self._tableGroup),
                expressions=self._buildColNames(self._df)
            ),
            expression=self._buildValues(self._df)
        )
    