import pandas as pd
import os

class Writer:
    """Class for writing data to various destinations"""

    def __init__(self, logger=None):
        """Initialize with optional logger"""
        self.logger = logger

    def write(self, df, output_path):
        """Write data to file"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            file_extension = os.path.splitext(output_path)[1].lower()

            if self.logger:
                self.logger.info(f"Attempting to write file: {output_path}")

            if file_extension == '.csv':
                df.to_csv(output_path, index=False)
            elif file_extension in ['.xlsx', '.xls']:
                df.to_excel(output_path, index=False)
            else:
                message = f"Unsupported file extension: {file_extension}"
                if self.logger:
                    self.logger.error(message)
                return False

            if self.logger:
                self.logger.info(f"Successfully wrote file with shape {df.shape} to: {output_path}")

            return True

        except Exception as e:
            error_msg = f"Error writing data to {output_path}: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return False