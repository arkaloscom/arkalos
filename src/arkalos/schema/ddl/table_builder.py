
from sqlglot import expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder
from arkalos.schema.ddl.column_builder import ColumnBuilder
from arkalos.schema.ddl.sequence_builder import SequenceBuilder
from arkalos.schema.types.index_type import IndexType



class TableBuilder(BaseQueryBuilder):

    _dialect: str
    _hasIdCol: bool
    _tableName: str
    _tableGroup: str|None
    _colExps: list[ColumnBuilder]
    _indexExps: list[exp.Constraint|exp.AddConstraint]
    _alter: bool



    def __init__(self, 
        table_name: str, 
        table_group: str|None = None, 
        alter: bool = False, 
        dialect: str = 'sqlite'
    ):
        
        self._dialect = dialect
        self._hasIdCol = False
        self._tableName = table_name
        self._tableGroup = table_group
        self._colExps = []
        self._indexExps = []
        self._alter = alter

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def col(self, column_name: str) -> 'ColumnBuilder':
        exp = ColumnBuilder(self._tableName, column_name, dialect=self._dialect, table_group=self._tableGroup)
        self._colExps.append(exp)
        return exp
    
    def hasIdCol(self) -> bool:
        for col in self._colExps:
            if col.isIdCol():
                return True
        return False
    
    

    def _createIndexName(self, 
        type: IndexType, 
        col_name: str|list[str], 
        index_name: str|None = None
    ) -> str:
        
        if index_name is not None:
            return index_name
        if isinstance(col_name, list):
            col_name = '_'.join(col_name)
        index_name = type.value + '__' + self._tableName + '__' + col_name
        if self._tableGroup:
            index_name = self._tableGroup + '__' + index_name
        return index_name

    def indexUnique(self, col_name: str|list[str], index_name: str|None = None):
        index_name = self._createIndexName(IndexType.UNIQUE, col_name, index_name)
        col_name_exps: list[exp.Identifier] = []
        if isinstance(col_name, list):
            col_name_exps = [exp.Identifier(this=col) for col in col_name]
        else:
            col_name_exps = [exp.Identifier(this=col_name)]

        index: exp.Constraint|exp.AddConstraint = exp.Constraint(
            this=exp.Identifier(this=index_name),
            expressions=[
                exp.UniqueColumnConstraint(
                    this=exp.Schema(
                        expressions=col_name_exps
                    )
                )
            ]
        )
        if self._alter:
            index = exp.AddConstraint(expressions=[index])
        self._indexExps.append(index)

    def foreignKey(self, 
        col_name: str, 
        ref_table: str,
        on_ref_col: str,
        ref_table_group: str|None = None,
        index_name: str|None = None
    ):
        
        index_name = self._createIndexName(IndexType.FOREIGN_KEY, col_name, index_name)
        index: exp.Constraint|exp.AddConstraint = exp.Constraint(
            this=exp.Identifier(this=index_name),
            expressions=[
                exp.ForeignKey(
                    expressions=[
                        exp.Identifier(this=col_name)
                    ],
                    reference=exp.Reference(
                        this=exp.Schema(
                            this=self.tableNameExpression(ref_table, ref_table_group),
                            expressions=[
                                exp.Identifier(this=on_ref_col)
                            ]
                        )
                    )
                )
            ]
        )
        if self._alter:
            index = exp.AddConstraint(expressions=[index])
        self._indexExps.append(index)
    


    def getExpression(self) -> exp.Alter|exp.Create:

        sql_exp: exp.Alter|exp.Create
        actions: list[exp.ColumnDef|exp.Constraint|exp.AddConstraint] = []
        for colExp in self._colExps:
            actions.append(colExp.getExpression())
        for indexExp in self._indexExps:
            actions.append(indexExp)

        if self._alter:
            sql_exp = exp.Alter(
                this=self.tableNameExpression(self._tableName, self._tableGroup),
                kind='TABLE',
                actions=actions
            )
        else:
            sql_exp = exp.Create(
                kind='TABLE',
                this=exp.Schema(
                    this=self.tableNameExpression(self._tableName, self._tableGroup),
                    expressions=actions
                )
            )

        # print(sql_exp.__repr__())
        
        return sql_exp
