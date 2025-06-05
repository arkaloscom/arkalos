
import sqlglot.expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder



class DeleteQueryBuilder(BaseQueryBuilder):

    _tableName: str
    _tableGroup: str|None
    _col: str|None
    _val: str|int|None

    def __init__(self, table_name: str, table_group: str|None = None):
        self._tableName = table_name
        self._tableGroup = table_group
        self._col = None
        self._val = None

    def where(self, col: str, val: int|str) -> 'DeleteQueryBuilder':
        self._col = col
        self._val = val
        return self

    def getExpression(self) -> exp.Delete:
        is_str = isinstance(self._val, str)
        sql_exp = exp.Delete(
            this=self.tableNameExpression(self._tableName, self._tableGroup),
            where=exp.Where(
                this=exp.EQ(
                    this=exp.Column(
                        this=exp.Identifier(this=self._col)
                    ),
                    expression=exp.Literal(this=str(self._val), is_string=is_str)
                )
            )
        )
        return sql_exp
