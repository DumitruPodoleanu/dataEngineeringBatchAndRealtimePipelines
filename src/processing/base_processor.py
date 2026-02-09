# src/processing/base_processor.py
import pandas as pd


class BaseProcessor:
    """Base class for data processors"""

    def __init__(self, logger=None):
        """Initialize with optional logger"""
        self.logger = logger

    def handle_missing_values(self, df, mandatory_columns=None):
        """Handle missing values in the dataset"""
        if self.logger:
            self.logger.info("Handling missing values")

        # Remove rows with missing values in mandatory columns
        if mandatory_columns:
            original_rows = len(df)
            df = df.dropna(subset=mandatory_columns)
            removed_rows = original_rows - len(df)

            if self.logger:
                self.logger.info(f"Removed {removed_rows} rows with missing mandatory values")

        return df

    def remove_columns(self, df, columns_to_remove=None):
        """Remove specified columns"""
        if not columns_to_remove:
            return df

        # Only drop columns that exist in the dataframe
        columns_to_remove = [col for col in columns_to_remove if col in df.columns]

        if columns_to_remove:
            if self.logger:
                self.logger.info(f"Removing columns: {columns_to_remove}")
            df = df.drop(columns=columns_to_remove)

        return df

    def process(self, df, validation_result=None):
        """Implement this in subclasses"""
        raise NotImplementedError("Subclasses must implement process()")