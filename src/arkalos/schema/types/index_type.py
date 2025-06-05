
from enum import StrEnum



class IndexType(StrEnum):
    INDEX = 'ix'
    UNIQUE = 'uq'
    FULLTEXT = 'ft'
    SPATIAL = 'gs'
    PRIMARY_KEY = 'pk'
    FOREIGN_KEY = 'fk'
