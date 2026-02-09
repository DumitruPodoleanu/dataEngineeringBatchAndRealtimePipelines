# src/data_io/reader.py
import pandas as pd
import os


class Reader:
    def __init__(self, logger=None):
        self.logger = logger

    def read(self, file_path):
        if self.logger:
            self.logger.info(f"Reading file: {file_path}")

        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                message = f"Unsupported file extension: {file_extension}"
                if self.logger:
                    self.logger.error(message)
                return None

            if self.logger:
                self.logger.info(f"Successfully read file with shape: {df.shape}")
            return df
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to read file '{file_path}': {str(e)}")
            return None
