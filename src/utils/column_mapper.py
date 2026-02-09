# src/utils/column_mapper.py
import re


def create_column_mapping(df_columns):
    """Create a mapping from actual column names to standardized names"""
    column_mapping = {}

    for col in df_columns:
        standardized = standardize_single_column(col)
        column_mapping[col] = standardized

    return column_mapping


def standardize_single_column(column_name):
    """Standardize a single column name"""
    # Replace special characters and normalize
    standardized = column_name.lower()
    standardized = re.sub(r'[^\w\s]', '', standardized)  # Remove special characters
    standardized = re.sub(r'\s+', '_', standardized)  # Replace spaces with underscores
    standardized = re.sub(r'_+', '_', standardized)  # Replace multiple underscores with single
    standardized = standardized.strip('_')  # Remove leading/trailing underscores

    # Handle specific cases
    if 'unnamed' in standardized:
        standardized = standardized.replace('_0', '_0').replace('.', '_')

    return standardized


def map_column_name(actual_column, mapping):
    """Map an actual column name to its standardized version"""
    return mapping.get(actual_column, standardize_single_column(actual_column))