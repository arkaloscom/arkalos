
from typing import Any
import json
from datetime import datetime

import sqlglot.expressions as exp
from abc import ABC, abstractmethod



class BaseQueryBuilder(ABC):
    
    @abstractmethod
    def getExpression(self) -> exp.Expression:
        pass

    def getExpressionList(self) -> list:
        raise NotImplementedError('getExpressionList() is not available for this query builder')

    def tableNameExpression(self, table_name: str, table_group: str|None = None) -> exp.Table:
        if table_group:
            return exp.Table(
                this=exp.Identifier(this=table_name),
                db=exp.Identifier(this=table_group)
            )
        else:
            return exp.Table(
                this=exp.Identifier(this=table_name)
            )
    
    def _expFromDataType(self, col_val: Any) -> exp.Expression:
        if col_val is None:
            return exp.Null()
        if isinstance(col_val, bool):
            return exp.Boolean(this=col_val)
        elif isinstance(col_val, datetime):
            return exp.Literal(this=str(col_val), is_string=True)
        elif isinstance(col_val, str):
            return exp.Literal(this=col_val, is_string=True)
        elif isinstance(col_val, (list, dict)):
            return exp.Literal(this=json.dumps(col_val), is_string=True)
        else:
            return exp.Literal(this=str(col_val), is_string=False)

    def sql(self, dialect='sqlite') -> str:
        return self.getExpression().sql(dialect=dialect, pretty=True) 
