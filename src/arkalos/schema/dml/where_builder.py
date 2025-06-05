
import sqlglot.expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder



class WhereBuilder(BaseQueryBuilder):

    _col: str
    _val: str|int

    def __init__(self, col: str, val: str|int):
        self._col = col
        self._val = val

    def getExpression(self) -> exp.Where:
        is_str = isinstance(self._val, str)
        return exp.Where(
            this=exp.EQ(
                this=exp.Column(
                    this=exp.Identifier(this=self._col)
                ),
                expression=exp.Literal(this=str(self._val), is_string=is_str)
            )
        )
