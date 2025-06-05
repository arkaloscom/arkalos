
import sqlglot.expressions as exp

from arkalos.schema.types.data_input_type import DataItemType

from arkalos.schema.base_query_builder import BaseQueryBuilder
from arkalos.schema.dml.column_setter_builder import ColumnSetterBuilder
from arkalos.schema.dml.where_builder import WhereBuilder



class UpdateQueryBuilder(BaseQueryBuilder):

    _tableName: str
    _tableGroup: str|None
    _col: str|None
    _val: str|int|None
    _item: DataItemType|None

    def __init__(self, table_name: str, table_group: str|None = None):
        self._tableName = table_name
        self._tableGroup = table_group
        self._col = None
        self._val = None
        self._item = None

    def update(self, item: DataItemType) -> 'UpdateQueryBuilder':
        self._item = item
        return self

    def where(self, col: str, val: int|str) -> 'UpdateQueryBuilder':
        self._col = col
        self._val = val
        return self

    def getExpression(self) -> exp.Update:
        if self._item is None or self._col is None or self._val is None:
            raise TypeError('UpdateQueryBuilder.getExpression(): use update() and where() first.')
        return exp.Update(
            this=self.tableNameExpression(self._tableName, self._tableGroup),
            expressions=ColumnSetterBuilder(self._item).getExpressionList(),
            where=WhereBuilder(self._col, self._val).getExpression()
        )
