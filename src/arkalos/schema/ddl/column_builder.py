
import sqlglot.expressions as exp

from arkalos.schema.base_query_builder import BaseQueryBuilder
from arkalos.schema.ddl.sequence_builder import SequenceBuilder
from arkalos.schema.types.sql_type import SQL_TYPE



class ColumnBuilder(BaseQueryBuilder):

    _dialect: str
    _isIdCol: bool
    _tableName: str
    _tableGroup: str|None
    _columnName: str
    _columnType: SQL_TYPE|None
    _columnTypeParams: list[exp.DataTypeParam|exp.DataType]
    _notNull: bool
    _defaultValue: str|None
    _defaultNow: bool
    _defaultFunction: str|None
    _defaultFunctionParam: str|None
    _comment: str|None

    _hasAutoIncrement: bool
    _hasIndexPrimary: bool
    _hasIndexUnique: bool
    _hasIndex: bool

    _foreignKeyTable: str|None
    _foreignKeyColumn: str|None



    def __init__(self, table_name: str, column_name: str, dialect: str = 'sqlite', table_group: str|None = None):
        self._tableName = table_name
        self._tableGroup = table_group
        self._dialect = dialect
        self._isIdCol = False
        self._columnName = column_name
        self._columnType = None
        self._columnTypeParams = []
        self._notNull = False
        self._defaultValue = None
        self._defaultNow = False
        self._defaultFunction = None
        self._defaultFunctionParam = None
        self._comment = None

        self._length = None
        self._decimalTotal = None
        self._decimalPlaces = None

        self._hasAutoIncrement = False
        self._hasIndexPrimary = False
        self._hasIndexUnique = False
        self._hasIndex = False

        self._foreignKeyTable = None
        self._foreignKeyColumn = None



    def isIdCol(self) -> bool:
        return self._isIdCol
    
    def type(self, col_type: SQL_TYPE) -> 'ColumnBuilder':
        self._columnType = col_type
        if self._dialect != 'sqlite' and col_type == SQL_TYPE.ARRAY:
            self._columnTypeParams.append(exp.DataType(this=SQL_TYPE.TEXT, nested=False))
        return self
    
    def id(self) -> 'ColumnBuilder':
        if self._dialect == 'sqlite':
            self._columnType = SQL_TYPE.BIGINT
        else:
            self._columnType = SQL_TYPE.UBIGINT
        if self._dialect == 'duckdb':
            self._defaultFunction = 'nextval'
            param = self._tableGroup + '.' + self._tableName if self._tableGroup else self._tableName
            self._defaultFunctionParam = param + SequenceBuilder.DEFAULT_SUFFIX
        else:
            self._hasAutoIncrement = True
        self._notNull = True
        self._hasIndexPrimary = True
        self._isIdCol = True
        return self
    
    def integer(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.INT
        return self
    
    def tinyInt(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.TINYINT
        return self  

    def smallInt(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.SMALLINT
        return self
    
    def bigInt(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.BIGINT
        return self
    
    def uInteger(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.UINT
        return self
    
    def uTinyInt(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.UTINYINT
        return self  

    def uSmallInt(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.USMALLINT
        return self
    
    def uBigInt(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.UBIGINT
        return self
    
    

    def decimal(self, total: int = 8, places: int = 2) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.DECIMAL
        self._columnTypeParams.append(exp.DataTypeParam(this=exp.Literal(this=total, is_string=False)))
        self._columnTypeParams.append(exp.DataTypeParam(this=exp.Literal(this=places, is_string=False)))
        return self




    def boolean(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.BOOLEAN
        return self
    


    def text(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.TEXT
        return self
    
    def string(self, length: int = 255) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.VARCHAR
        self._columnTypeParams.append(exp.DataTypeParam(this=exp.Literal(this=length, is_string=False)))
        return self
    

    def date(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.DATE
        return self

    def datetime(self) -> 'ColumnBuilder':
        self._columnType = SQL_TYPE.DATETIME
        return self


    
    def notNull(self) -> 'ColumnBuilder':
        self._notNull = True
        return self
    
    def nullable(self, value: bool = False) -> 'ColumnBuilder':
        self._notNull = not value
        return self
    
    def default(self, default_value: str) -> 'ColumnBuilder':
        self._defaultValue = default_value
        return self
    
    def defaultNow(self) -> 'ColumnBuilder':
        self._defaultNow = True
        return self
    
    def defaultFunction(self, function_name: str, param: str) -> 'ColumnBuilder':
        self._defaultFunction = function_name
        self._defaultFunctionParam = param
        return self


    
    def getExpression(self) -> exp.ColumnDef:
        constraints: list[exp.ColumnConstraint] = []

        if self._hasIndexPrimary:
            constraints.append(exp.ColumnConstraint(
                kind=exp.PrimaryKeyColumnConstraint()
            ))

        if self._hasAutoIncrement:
            constraints.append(exp.ColumnConstraint(
                kind=exp.AutoIncrementColumnConstraint()
            ))

        if self._notNull:
            constraints.append(exp.ColumnConstraint(
                kind=exp.NotNullColumnConstraint()
            ))

        if self._defaultValue:
            is_string = self._columnType in exp.DataType.TEXT_TYPES
            constraints.append(exp.ColumnConstraint(
                kind=exp.DefaultColumnConstraint(
                    this=exp.Literal(this=self._defaultValue, is_string=is_string)
                )
            ))
        
        if self._defaultNow:
            constraints.append(exp.ColumnConstraint(
                kind=exp.DefaultColumnConstraint(
                    this=exp.CurrentTimestamp()
                )
            ))

        if self._defaultFunction:
            constraints.append(exp.ColumnConstraint(
                kind=exp.DefaultColumnConstraint(
                    this=exp.Anonymous(
                        this=self._defaultFunction,
                        expressions=[
                            exp.Literal(this=self._defaultFunctionParam, is_string=True)
                        ]
                    )
                )
            ))

        return exp.ColumnDef(
            this=exp.Column(this=self._columnName),
            kind=exp.DataType(this=self._columnType, expressions=self._columnTypeParams),
            constraints=constraints
        )
