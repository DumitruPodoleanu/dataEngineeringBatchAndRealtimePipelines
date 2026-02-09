# src/validation/base_validator.py
import pandas as pd

class BaseValidator:

    def __init__(self, logger=None):
        self.logger = logger

    def validate_columns(self, df, expected_columns, mandatory_columns):
        actual_columns = set(df.columns)
        expected_columns = set(expected_columns)
        mandatory_columns = set(mandatory_columns)

        # Check for missing mandatory columns
        missing_mandatory = mandatory_columns - actual_columns

        # Check for missing optional columns
        missing_optional = (expected_columns - mandatory_columns) - actual_columns

        # Check for unexpected columns
        unexpected = actual_columns - expected_columns

        # Compile results
        results = {
            "missing_mandatory": list(missing_mandatory),
            "missing_optional": list(missing_optional),
            "unexpected": list(unexpected)
        }

        is_valid = len(missing_mandatory) == 0

        # Log validation results
        if self.logger:
            if is_valid:
                self.logger.info("Column validation passed")
            else:
                self.logger.error(f"Column validation failed: {results}")

        return is_valid, results

    def validate_data_types(self, df, dtype_mapping):
        type_issues = {}

        for column, expected_type in dtype_mapping.items():
            if column in df.columns:
                # Skip validation for missing values
                mask = df[column].notna()

                if mask.sum() > 0:
                    sample = df.loc[mask, column].iloc[0]

                    # Check if type is compatible
                    try:
                        if expected_type == 'datetime64[ns]':
                            pd.to_datetime(df.loc[mask, column])
                        else:
                            df.loc[mask, column].astype(expected_type)
                    except:
                        type_issues[column] = f"Expected {expected_type}, found {type(sample)}"

        is_valid = len(type_issues) == 0

        # Log validation results
        if self.logger:
            if is_valid:
                self.logger.info("Data type validation passed")
            else:
                self.logger.error(f"Data type validation failed: {type_issues}")

        return is_valid, type_issues

    def validate(self, df):
        raise NotImplementedError("Subclasses must implement validate()")