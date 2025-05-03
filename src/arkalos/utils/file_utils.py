
import sys
import re
import os
from typing import Iterator
import json



def escape_filename(filename):
    # Remove characters that are invalid for filenames in most operating systems
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    return re.sub(invalid_chars, '_', filename)

def create_folder(file_path_name):
    folder_path = os.path.dirname(file_path_name)
    os.makedirs(folder_path, exist_ok=True)



class FileReader:
    '''
    A versatile file reader class that can efficiently read files line by line
    from either the beginning or the end, with built-in support for pagination.
    Optimized for large files using chunk-based reading and designed for
    excellent developer experience.
    '''

    file_path: str
    encoding: str
    buffer_size: int

    _file_exists: bool
    _file_size: int
    _total_lines: int|None
    
    def __init__(self, file_path: str, encoding: str = 'utf-8', buffer_size: int = 8192):
        '''
        Initialize the file reader.
        
        Args:
            file_path (str): Path to the file to read.
            encoding (str): Text encoding of the file. Defaults to UTF-8.
            buffer_size (int): Size of chunks to read at once.
        '''
        self.file_path = file_path
        self.encoding = encoding
        self.buffer_size = buffer_size
        self._file_exists = os.path.exists(file_path)
        self._file_size = os.path.getsize(file_path) if self._file_exists else 0
        self._total_lines = None
        
    def exists(self) -> bool:
        '''Check if the file exists.'''
        return self._file_exists
        
    def getSize(self) -> int:
        '''Get the file size in bytes.'''
        return self._file_size
    
    def countLines(self) -> int:
        '''
        Count the total number of lines in the file.
        This method caches the result for future calls.
        
        Returns:
            int: Total number of lines in the file.
        '''
        if self._total_lines is not None:
            return self._total_lines
            
        if not self._file_exists:
            return 0
            
        count = 0
        try:
            with open(self.file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.buffer_size), b''):
                    count += chunk.count(b'\n')
                    
                # If file doesn't end with newline, add one more line
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b'\n' and self._file_size > 0:
                    count += 1
        except (IOError, OSError):
            return 0
            
        self._total_lines = count
        return count
    
    def countPages(self, page_size: int = 20) -> int:
        '''
        Calculate the total number of pages based on line count and page size.
        
        Args:
            page_size (int): Number of lines per page.
            
        Returns:
            int: Total number of pages.
        '''
        if page_size <= 0:
            return 0
            
        total_lines = self.countLines()
        return (total_lines + page_size - 1) // page_size
        
    def readForward(self) -> Iterator[str]:
        '''
        Read the file line by line from the beginning (standard direction).
        More memory efficient than reading the entire file at once.
        
        Yields:
            str: Each line from the file, decoded and stripped of whitespace.
        '''
        if not self._file_exists:
            return
            
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                for line in f:
                    yield line.rstrip('\r\n')
        except (IOError, UnicodeDecodeError) as e:
            print(f'Error reading file {self.file_path}: {e}', file=sys.stderr)
            return
            
    def readBackward(self) -> Iterator[str]:
        '''
        Read the file line by line from the end (reverse direction).
        Optimized for large files.
        
        Yields:
            str: Each line from the file, decoded and stripped of whitespace.
        '''
        if not self._file_exists or self._file_size == 0:
            return

        try:
            with open(self.file_path, 'rb') as f:
                remaining_bytes = self._file_size
                buffer = bytearray()
                
                while remaining_bytes > 0:
                    bytes_to_read = min(self.buffer_size, remaining_bytes)
                    f.seek(remaining_bytes - bytes_to_read, os.SEEK_SET)
                    chunk = f.read(bytes_to_read)
                    
                    # Prepend the chunk to buffer
                    buffer[0:0] = chunk
                    remaining_bytes -= bytes_to_read
                    
                    # Find and process lines in the buffer
                    newline_pos = buffer.rfind(b'\n')
                    while newline_pos != -1:
                        # Extract the line (from after newline to end of buffer)
                        line_bytes = buffer[newline_pos + 1:]
                        # Remove the extracted line and the newline from buffer
                        del buffer[newline_pos:]
                        
                        try:
                            line = line_bytes.decode(self.encoding).rstrip('\r\n')
                            yield line
                        except UnicodeDecodeError as e:
                            print(f'Error reading file {self.file_path}: {e}', file=sys.stderr)
                            return
                            
                        # Find the next newline searching backwards
                        newline_pos = buffer.rfind(b'\n')
                
                # Handle the first line if there's no newline at the beginning
                if buffer:
                    try:
                        line = buffer.decode(self.encoding).rstrip('\r\n')
                        yield line
                    except UnicodeDecodeError as e:
                        print(f'Error reading file {self.file_path}: {e}', file=sys.stderr)
                        return
        except IOError as e:
            print(f'Error reading file {self.file_path}: {e}', file=sys.stderr)
            return
            
    def getPage(self, page: int = 1, page_size: int = 20, reverse: bool = False) -> list[str]:
        '''
        Get a specific page of lines from the file.
        
        Args:
            page (int): The page number, starting from 1.
            page_size (int): Number of lines per page.
            reverse (bool): If True, read from the end of the file (newest first).
                           If False, read from the beginning (oldest first).
            
        Returns:
            List[str]: A list of lines from the requested page.
        '''
        if not self._file_exists:
            return []
            
        if page < 1:
            page = 1
        
        if reverse:
            lines_to_skip = (page - 1) * page_size
            collected_lines = []
            line_count = 0
            
            for line in self.readBackward():
                line_count += 1
                if line_count > lines_to_skip:
                    collected_lines.append(line)
                    if len(collected_lines) >= page_size:
                        break
                
            return collected_lines
        else:
            start_line = (page - 1) * page_size
            end_line = start_line + page_size
            
            result = []
            for i, line in enumerate(self.readForward()):
                if i >= start_line:
                    result.append(line)
                if i >= end_line - 1:
                    break
                    
        return result
    
    def getPageWithMetadata(self, page: int = 1, page_size: int = 20, reverse: bool = False) -> tuple[list[str], dict]:
        '''
        Get a specific page of lines with additional pagination metadata.
        
        Args:
            page (int): The page number, starting from 1.
            page_size (int): Number of lines per page.
            reverse (bool): If True, read from the end of the file (newest first).
                           If False, read from the beginning (oldest first).
            
        Returns:
            tuple[list[str], dict]: A tuple containing:
                - List of lines from the requested page
                - Dictionary with pagination metadata:
                    - current_page: Current page number
                    - page_size: Number of lines per page
                    - total_pages: Total number of pages
                    - total_lines: Total number of lines in the file
                    - has_next: Whether there is a next page
                    - has_prev: Whether there is a previous page
        '''
        # Get page content
        page_content = self.getPage(page, page_size, reverse)
        
        # Calculate metadata
        total_lines = self.countLines()
        total_pages = self.countPages(page_size)
        
        metadata = {
            'current_page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_lines': total_lines,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
        
        return page_content, metadata
        
    def getJSONPage(self, page: int = 1, page_size: int = 20, reverse: bool = False) -> list[dict]:
        '''
        Get a specific page of lines from a JSON Lines file and parse them.
        
        Args:
            page (int): The page number, starting from 1.
            page_size (int): Number of lines per page.
            reverse (bool): If True, read from the end of the file (newest first).
                           If False, read from the beginning (oldest first).
            
        Returns:
            List[dict]: A list of parsed JSON objects from the requested page.
        '''
        lines = self.getPage(page, page_size, reverse)
        result = []
        
        for line in lines:
            if not line.strip():
                continue
                
            try:
                obj = json.loads(line)
                result.append(obj)
            except json.JSONDecodeError as e:
                print(f'Error reading file {self.file_path}: {e}', file=sys.stderr)
                return []
                
        return result
