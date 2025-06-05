
from typing import Any
from datetime import datetime
import json

import sqlglot.expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder
from arkalos.schema.types.data_input_type import DataItemType, input_item_to_dict



class ColumnSetterBuilder(BaseQueryBuilder):

    _item: DataItemType

    def __init__(self, item: DataItemType):
        self._item = item
    
    def _buildColumns(self) -> list[exp.EQ]:
        item_dict = input_item_to_dict(self._item)
        col_exps = []
        for col in item_dict:
            col_exps.append(self._buildColumnSetter(col, item_dict[col]))
        return col_exps
    
    def _buildColumnSetter(self, col_name: str, col_val: Any) -> exp.EQ:
        return exp.EQ(
            this=exp.Column(
                this=exp.Identifier(this=col_name, quoted=False)
            ),
            expression=self._expFromDataType(col_val)
        )

    def getExpression(self):
        raise NotImplementedError('getExpression() is not available for the ColumnSetterBuilder' \
        'Use getExpressionList() instead')

    def getExpressionList(self) -> list[exp.EQ]:
        return self._buildColumns()
