
import logging
import os

# --- Custom File Handler ---
class FileHandler(logging.FileHandler):
    """
    A FileHandler that checks if the file exists before emitting a log record.
    If the file doesn't exist (e.g., deleted externally), it attempts to
    recreate it.
    """
    def emit(self, record):
        """
        Emit a record.

        Check if the log file exists. If not, close the stream and attempt
        to reopen it (which creates the file). Then, emit the record.
        Handle potential errors during file operations.
        """
        if not os.path.exists(self.baseFilename):
            try:
                # Close the existing stream if it's open
                if self.stream:
                    self.stream.close()
                    self.stream = None # Set stream to None so _open() creates a new one

                # Re-open the stream - this should recreate the file
                self.stream = self._open()
            except Exception as e:
                print('Error:', e)
                # Handle exceptions during file reopening (e.g., permission errors)
                # Depending on requirements, you might want to log this error
                # to stderr or another fallback mechanism.
                # For now, we'll let the standard handler try and potentially fail.
                pass # Or handle error more explicitly

        # Now call the original emit method
        super().emit(record)
