
import sqlglot.expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder

class SequenceBuilder(BaseQueryBuilder):

    DEFAULT_SUFFIX: str = '_seq'

    _tableName: str
    _tableGroup: str|None

    def __init__(self, table_name: str, table_group: str|None = None):
        self._tableName = table_name
        self._tableGroup = table_group

    def getExpression(self):
        return exp.Create(
            this=self.tableNameExpression(self._tableName + self.DEFAULT_SUFFIX, self._tableGroup),
            kind='SEQUENCE',
            exists=True
        )
