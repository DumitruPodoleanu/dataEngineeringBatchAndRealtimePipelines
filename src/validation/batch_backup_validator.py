# src/validation/batch_backup_validator.py
import pandas as pd
import numpy as np
from src.validation.base_validator import BaseValidator
from config.validation_rules import NASHVILLE_COLUMNS
class BatchBackupValidator(BaseValidator):

    def validate_derived_columns(self, df):

        expected_derived_columns = NASHVILLE_COLUMNS.get('derived_columns', [])
        actual_columns = set(df.columns)
        missing_columns = set(expected_derived_columns) - actual_columns

        if missing_columns:
            if self.logger:
                self.logger.error(f"Missing derived columns: {missing_columns}")
            return False, {"missing_derived_columns": list(missing_columns)}

        column_issues = {}

        # Validate each derived column has appropriate values
        for column in expected_derived_columns:
            if column in df.columns:
                # Check for null values
                null_count = df[column].isna().sum()
                if null_count > 0 and self.logger:
                    self.logger.warning(f"Column '{column}' has {null_count} null values")

                # Check for specific column validations
                if column == 'pricepersqft':
                    if (df[column] < 0).any():
                        column_issues[column] = "Contains negative values"

                elif column == 'propertyage':
                    if (df[column] < 0).any():
                        column_issues[column] = "Contains negative values"
                    if (df[column] > 300).any():  # Unlikely to have buildings older than 300 years
                        column_issues[column] = "Contains unreasonably high values"

                elif column == 'landtobuildingratio':
                    if (df[column] < 0).any():
                        column_issues[column] = "Contains negative values"

                elif column == 'salepricecategory':
                    valid_categories = {'Low', 'Medium', 'High', 'Unknown'}
                    actual_categories = set(df[column].dropna().unique())
                    invalid_categories = actual_categories - valid_categories
                    if invalid_categories:
                        column_issues[column] = f"Contains invalid categories: {invalid_categories}"

                elif column == 'price_outlier_status':
                    valid_statuses = {'Normal', 'High Outlier', 'Low Outlier'}
                    actual_statuses = set(df[column].dropna().unique())
                    invalid_statuses = actual_statuses - valid_statuses
                    if invalid_statuses:
                        column_issues[column] = f"Contains invalid statuses: {invalid_statuses}"

                elif column == 'neighborhood_price_index':
                    valid_indices = {'Significantly Above Average', 'Above Average', 'Average',
                                     'Below Average', 'Significantly Below Average', 'Unknown'}
                    actual_indices = set(df[column].dropna().unique())
                    invalid_indices = actual_indices - valid_indices
                    if invalid_indices:
                        column_issues[column] = f"Contains invalid indices: {invalid_indices}"

                elif column == 'value_condition_proxy':
                    valid_conditions = {'Above Average for Age/Location', 'Average for Age/Location',
                                        'Below Average for Age/Location', 'Unknown'}
                    actual_conditions = set(df[column].dropna().unique())
                    invalid_conditions = actual_conditions - valid_conditions
                    if invalid_conditions:
                        column_issues[column] = f"Contains invalid conditions: {invalid_conditions}"

        is_valid = len(column_issues) == 0

        if self.logger:
            if is_valid:
                self.logger.info("All derived columns validated successfully")
            else:
                self.logger.error(f"Issues found in derived columns: {column_issues}")

        return is_valid, {"column_issues": column_issues}

    def validate(self, df):

        if self.logger:
            self.logger.info("Starting backup validation for processed data")

        # Validate derived columns
        derived_cols_valid, derived_cols_results = self.validate_derived_columns(df)

        # Overall validation result
        is_valid = derived_cols_valid

        validation_results = {
            "derived_columns_validation": derived_cols_results,
            "is_valid": is_valid
        }

        if self.logger:
            if is_valid:
                self.logger.info("Processed data passed backup validation")
            else:
                self.logger.error("Processed data failed backup validation")

        return is_valid, validation_results