
import logging

class InfoFilter(logging.Filter):
    '''Filter to only allow records with level <= INFO.'''
    
    def filter(self, record):
        '''Return True if record level is <= INFO.'''
        
        return record.levelno <= logging.INFO
