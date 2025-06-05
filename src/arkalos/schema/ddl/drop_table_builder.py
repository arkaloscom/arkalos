
import sqlglot.expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder



class DropTableBuilder(BaseQueryBuilder):

    _tableName: str

    def __init__(self, table_name: str, table_group: str|None = None):
        self._tableName = table_name
        self._tableGroup = table_group

    def getExpression(self) -> exp.Drop:
        return exp.Drop(
            kind='TABLE',
            exists=True,
            this=self.tableNameExpression(self._tableName, self._tableGroup)
        )
