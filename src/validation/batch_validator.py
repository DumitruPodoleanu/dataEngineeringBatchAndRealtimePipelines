# src/validation/batch_validator.py
import pandas as pd
import numpy as np
from datetime import datetime
from src.validation.base_validator import BaseValidator
from config.validation_rules import NASHVILLE_COLUMNS

class BatchValidator(BaseValidator):

    def __init__(self, logger=None):
        super().__init__(logger)
        self.validation_errors = []
        self.validation_summary = {
            'total_errors': 0,
            'error_types': {},
            'affected_rows': set(),
            'error_details': []
        }

    def standardize_column_names(self, df):
        df_copy = df.copy()
        # Replace special characters and normalize column names
        df_copy.columns = df_copy.columns.str.replace(" ", "_").str.replace("/", "_").str.replace("-", "_")
        df_copy.columns = df_copy.columns.str.replace("#", "").str.replace("__", "_").str.lower()
        # Clean up unnamed columns
        df_copy.columns = [col.replace('unnamed:_', 'unnamed_') for col in df_copy.columns]
        return df_copy

    def validate_data_integrity(self, df):
        errors = []
        df_std = self.standardize_column_names(df)

        # 1. Validate Sale Price
        if 'saleprice' in df_std.columns:
            # Check for negative values
            negative_prices = df_std[df_std['saleprice'] < 0]
            if not negative_prices.empty:
                error_details = []
                for idx, row in negative_prices.iterrows():
                    error_details.append(f"Row {idx}: Sale Price = {row['saleprice']}")

                errors.append({
                    'type': 'Negative Sale Price',
                    'count': len(negative_prices),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(negative_prices.index)

            # Check for unrealistic values (> $10M)
            unrealistic_prices = df_std[df_std['saleprice'] > 10000000]
            if not unrealistic_prices.empty:
                error_details = []
                for idx, row in unrealistic_prices.iterrows():
                    error_details.append(f"Row {idx}: Sale Price = {row['saleprice']}")

                errors.append({
                    'type': 'Unrealistic Sale Price (> $10M)',
                    'count': len(unrealistic_prices),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(unrealistic_prices.index)

        # 2. Validate Year Built
        if 'yearbuilt' in df_std.columns:
            current_year = datetime.now().year

            # Check for future years
            future_years = df_std[df_std['yearbuilt'] > current_year]
            if not future_years.empty:
                error_details = []
                for idx, row in future_years.iterrows():
                    error_details.append(f"Row {idx}: Year Built = {row['yearbuilt']}")

                errors.append({
                    'type': 'Future Year Built',
                    'count': len(future_years),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(future_years.index)

            # Check for unreasonably old years (< 1800)
            old_years = df_std[df_std['yearbuilt'] < 1800]
            if not old_years.empty:
                error_details = []
                for idx, row in old_years.iterrows():
                    error_details.append(f"Row {idx}: Year Built = {row['yearbuilt']}")

                errors.append({
                    'type': 'Unrealistic Year Built (< 1800)',
                    'count': len(old_years),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(old_years.index)

        # 3. Validate Bedrooms/Bathrooms
        if 'bedrooms' in df_std.columns:
            # Check for negative bedrooms
            negative_bedrooms = df_std[df_std['bedrooms'] < 0]
            if not negative_bedrooms.empty:
                error_details = []
                for idx, row in negative_bedrooms.iterrows():
                    error_details.append(f"Row {idx}: Bedrooms = {row['bedrooms']}")

                errors.append({
                    'type': 'Negative Bedrooms',
                    'count': len(negative_bedrooms),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(negative_bedrooms.index)

            # Check for unrealistic numbers (> 20)
            too_many_bedrooms = df_std[df_std['bedrooms'] > 20]
            if not too_many_bedrooms.empty:
                error_details = []
                for idx, row in too_many_bedrooms.iterrows():
                    error_details.append(f"Row {idx}: Bedrooms = {row['bedrooms']}")

                errors.append({
                    'type': 'Unrealistic Bedrooms (> 20)',
                    'count': len(too_many_bedrooms),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(too_many_bedrooms.index)

        # 4. Validate Bathrooms
        for bath_col in ['fullbath', 'halfbath']:
            if bath_col in df_std.columns:
                # Check for negative bathrooms
                negative_baths = df_std[df_std[bath_col] < 0]
                if not negative_baths.empty:
                    error_details = []
                    for idx, row in negative_baths.iterrows():
                        error_details.append(f"Row {idx}: {bath_col} = {row[bath_col]}")

                    errors.append({
                        'type': f'Negative {bath_col}',
                        'count': len(negative_baths),
                        'details': error_details
                    })
                    self.validation_summary['affected_rows'].update(negative_baths.index)

                # Check for unrealistic numbers (> 10)
                too_many_baths = df_std[df_std[bath_col] > 10]
                if not too_many_baths.empty:
                    error_details = []
                    for idx, row in too_many_baths.iterrows():
                        error_details.append(f"Row {idx}: {bath_col} = {row[bath_col]}")

                    errors.append({
                        'type': f'Unrealistic {bath_col} (> 10)',
                        'count': len(too_many_baths),
                        'details': error_details
                    })
                    self.validation_summary['affected_rows'].update(too_many_baths.index)

        # 5. Validate Acreage
        if 'acreage' in df_std.columns:
            # Check for negative values
            negative_acreage = df_std[df_std['acreage'] < 0]
            if not negative_acreage.empty:
                error_details = []
                for idx, row in negative_acreage.iterrows():
                    error_details.append(f"Row {idx}: Acreage = {row['acreage']}")

                errors.append({
                    'type': 'Negative Acreage',
                    'count': len(negative_acreage),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(negative_acreage.index)

            # Check for very large values (> 1000 acres)
            large_acreage = df_std[df_std['acreage'] > 1000]
            if not large_acreage.empty:
                error_details = []
                for idx, row in large_acreage.iterrows():
                    error_details.append(f"Row {idx}: Acreage = {row['acreage']}")

                errors.append({
                    'type': 'Unrealistic Acreage (> 1000 acres)',
                    'count': len(large_acreage),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(large_acreage.index)

        # 6. Validate Land Value, Building Value, Total Value
        value_columns = ['landvalue', 'buildingvalue', 'totalvalue']
        for col in value_columns:
            if col in df_std.columns:
                # Check for negative values
                negative_values = df_std[df_std[col] < 0]
                if not negative_values.empty:
                    error_details = []
                    for idx, row in negative_values.iterrows():
                        error_details.append(f"Row {idx}: {col} = {row[col]}")

                    errors.append({
                        'type': f'Negative {col}',
                        'count': len(negative_values),
                        'details': error_details
                    })
                    self.validation_summary['affected_rows'].update(negative_values.index)

        # 7. Validate Total Value = Land Value + Building Value
        if all(col in df_std.columns for col in ['landvalue', 'buildingvalue', 'totalvalue']):
            expected_total = df_std['landvalue'] + df_std['buildingvalue']
            value_mismatch = df_std[np.abs(df_std['totalvalue'] - expected_total) > 1]  # Allow for rounding

            if not value_mismatch.empty:
                error_details = []
                for idx, row in value_mismatch.iterrows():
                    error_details.append(
                        f"Row {idx}: Land Value = {row['landvalue']}, "
                        f"Building Value = {row['buildingvalue']}, "
                        f"Expected Total = {row['landvalue'] + row['buildingvalue']}, "
                        f"Actual Total = {row['totalvalue']}"
                    )

                errors.append({
                    'type': 'Total Value Mismatch',
                    'count': len(value_mismatch),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(value_mismatch.index)

        # 8. Validate Duplicate Records
        duplicate_cols = ['parcelid'] if 'parcelid' in df_std.columns else []
        if duplicate_cols:
            duplicates = df_std[df_std.duplicated(subset=duplicate_cols, keep=False)]
            if not duplicates.empty:
                error_details = []
                for idx, row in duplicates.iterrows():
                    error_details.append(f"Row {idx}: Parcel ID = {row['parcelid']}")

                errors.append({
                    'type': 'Duplicate Parcel ID',
                    'count': len(duplicates),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(duplicates.index)

        # 9. Validate Date Format and Range
        if 'saledate' in df_std.columns:
            # Check for invalid dates
            df_std['saledate'] = pd.to_datetime(df_std['saledate'], errors='coerce')
            invalid_dates = df_std[df_std['saledate'].isna()]

            if not invalid_dates.empty:
                error_details = []
                for idx, row in invalid_dates.iterrows():
                    error_details.append(f"Row {idx}: Invalid or missing sale date")

                errors.append({
                    'type': 'Invalid Sale Date',
                    'count': len(invalid_dates),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(invalid_dates.index)

            # Check for future dates
            future_dates = df_std[df_std['saledate'] > datetime.now()]
            if not future_dates.empty:
                error_details = []
                for idx, row in future_dates.iterrows():
                    error_details.append(f"Row {idx}: Sale Date = {row['saledate']}")

                errors.append({
                    'type': 'Future Sale Date',
                    'count': len(future_dates),
                    'details': error_details
                })
                self.validation_summary['affected_rows'].update(future_dates.index)

        # 10. Validate Missing Values in Mandatory Columns (Warning only)
        mandatory_columns_std = [col.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
                                 for col in NASHVILLE_COLUMNS['mandatory_columns']]

        missing_value_warnings = []
        for col in mandatory_columns_std:
            if col in df_std.columns:
                missing_values = df_std[df_std[col].isna()]
                if not missing_values.empty:
                    warning_details = []
                    for idx, _ in missing_values.iterrows():
                        warning_details.append(f"Row {idx}: Missing {col}")

                    missing_value_warnings.append({
                        'type': f'Missing Mandatory Column: {col}',
                        'count': len(missing_values),
                        'details': warning_details
                    })

                    if self.logger:
                        self.logger.warning((
                            f"Found {len(missing_values)} missing values in mandatory column '{col}'. These rows will be removed during processing."))



        # Update validation summary
        self.validation_summary['total_errors'] = sum(error['count'] for error in errors)
        for error in errors:
            error_type = error['type']
            if error_type not in self.validation_summary['error_types']:
                self.validation_summary['error_types'][error_type] = 0
            self.validation_summary['error_types'][error_type] += error['count']
            self.validation_summary['error_details'].extend(error['details'])

        return errors

    def display_validation_results(self, errors):
        """Display validation results in a clear, readable format"""
        if not errors:
            if self.logger:
                self.logger.info(("All validation checks passed"))
            return

        # Display summary
        if self.logger:
            self.logger.error(("=" * 80))
            self.logger.error(("VALIDATION FAILURES DETECTED"))
            self.logger.error(("=" * 80))
            self.logger.error((f"Total Errors Found: {self.validation_summary['total_errors']}"))
            self.logger.error((f"Affected Rows: {len(self.validation_summary['affected_rows'])}"))
            self.logger.error(("-" * 80))

        # Display error type summary
        if self.logger:
            self.logger.error(("ERROR SUMMARY BY TYPE:"))
            for error_type, count in self.validation_summary['error_types'].items():
                self.logger.error((f"  • {error_type}: {count} instances"))
            self.logger.error(("-" * 80))

        # Display detailed errors
        if self.logger:
            self.logger.error(("DETAILED ERRORS:"))
            for error in errors:
                self.logger.error((f"\n{error['type']} ({error['count']} instances):"))
                # Show first 10 examples
                for detail in error['details'][:10]:
                    self.logger.error((f"  {detail}"))
                if len(error['details']) > 10:
                    self.logger.error((f"  ... and {len(error['details']) - 10} more"))
            self.logger.error(("=" * 80))

    def validate(self, df):
        """Validate the Nashville Housing dataset"""
        if self.logger:
            self.logger.info("Starting validation for Nashville Housing dataset")

        # First standardize column names for validation
        df_std = self.standardize_column_names(df)

        # Standardize expected columns
        all_columns_std = [col.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
                           for col in NASHVILLE_COLUMNS['all_columns']]
        mandatory_columns_std = [col.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
                                 for col in NASHVILLE_COLUMNS['mandatory_columns']]

        # Validate columns
        cols_valid, cols_results = self.validate_columns(
            df_std,
            all_columns_std,
            mandatory_columns_std
        )

        # Validate data integrity
        integrity_errors = self.validate_data_integrity(df)

        # Display results
        self.display_validation_results(integrity_errors)

        # Overall validation result
        is_valid = len(integrity_errors) == 0

        validation_results = {
            "column_validation": cols_results,
            "integrity_errors": integrity_errors,
            "validation_summary": self.validation_summary,
            "is_valid": is_valid
        }

        if self.logger:
            if is_valid:
                self.logger.info(("Nashville Housing dataset passed validation"))
            else:
                self.logger.error(("Nashville Housing dataset failed validation"))
                self.logger.error((
                    f"Found {self.validation_summary['total_errors']} errors affecting {len(self.validation_summary['affected_rows'])} rows"))

        return is_valid, validation_results