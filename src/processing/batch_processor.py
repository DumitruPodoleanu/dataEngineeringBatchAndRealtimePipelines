# src/processing/batch_processor.py
import pandas as pd
import numpy as np
from datetime import datetime
from src.processing.base_processor import BaseProcessor
from config.batch_config import BATCH_CONFIG
from config.validation_rules import NASHVILLE_COLUMNS


class BatchProcessor(BaseProcessor):
    """Processor for Nashville Housing dataset"""

    def standardize_column_names(self, df):
        """Standardize column names to lowercase with underscores"""
        if self.logger:
            self.logger.info("Standardizing column names")

        df.columns = df.columns.str.replace(" ", "_").str.replace("/", "_").str.replace("-", "_").str.lower()
        return df

    def handle_missing_values(self, df, mandatory_columns=None):
        """Handle missing values in the dataset"""
        if self.logger:
            self.logger.info("Handling missing values in mandatory columns")

        # Find matching columns by standardizing names
        matching_columns = []
        for mandatory_col in mandatory_columns or []:
            std_mandatory = mandatory_col.lower()

            # Simple standardization for column matching
            for actual_col in df.columns:
                # Standardize the actual column name for comparison
                std_actual = str(actual_col).lower().replace(" ", "_").replace("/", "_").replace("-", "_")

                if std_mandatory in std_actual or std_actual in std_mandatory:
                    matching_columns.append(actual_col)
                    break

        # Remove rows with missing values in matched mandatory columns
        if matching_columns:
            original_rows = len(df)
            df = df.dropna(subset=matching_columns, how='any')
            removed_rows = original_rows - len(df)

            if self.logger:
                self.logger.info(f"Removed {removed_rows} rows with missing mandatory values")
                for col in matching_columns:
                    missing_count = (original_rows - df[col].count())
                    if missing_count > 0:
                        self.logger.info(f"  - Column '{col}': removed {missing_count} missing values")
        else:
            if self.logger:
                self.logger.warning("No matching mandatory columns found to check for missing values")

        return df

    def add_derived_columns(self, df):
        """Add derived columns to the dataset"""
        if self.logger:
            self.logger.info("Adding derived columns")

        try:
            # Map column name to standardized version
            if 'sale_date' in df.columns:
                saledate_col = 'sale_date'
            elif 'saledate' in df.columns:
                saledate_col = 'saledate'
            else:
                saledate_col = None

            if saledate_col:
                # Ensure sale date is datetime
                df[saledate_col] = pd.to_datetime(df[saledate_col], errors='coerce')

                # Sale year and month
                df['saleyear'] = df[saledate_col].dt.year
                df['salemonth'] = df[saledate_col].dt.month
            else:
                self.logger.warning("No sale date column found. Skipping date-related derived columns.")
                df['saleyear'] = None
                df['salemonth'] = None

            # Map year built column
            if 'year_built' in df.columns:
                yearbuilt_col = 'year_built'
            elif 'yearbuilt' in df.columns:
                yearbuilt_col = 'yearbuilt'
            else:
                yearbuilt_col = None

            if yearbuilt_col:
                # Property Age
                df[yearbuilt_col] = pd.to_numeric(df[yearbuilt_col], errors='coerce')
                if 'saleyear' in df.columns and df['saleyear'].notna().any():
                    df['propertyage'] = df['saleyear'] - df[yearbuilt_col]
                    df.loc[df['propertyage'] < 0, 'propertyage'] = 0  # Handle potential errors
                else:
                    df['propertyage'] = None
            else:
                df['propertyage'] = None

            # Map sale price column
            if 'sale_price' in df.columns:
                saleprice_col = 'sale_price'
            elif 'saleprice' in df.columns:
                saleprice_col = 'saleprice'
            else:
                saleprice_col = None

            # Map finished area column
            if 'finished_area' in df.columns:
                finishedarea_col = 'finished_area'
            elif 'finishedarea' in df.columns:
                finishedarea_col = 'finishedarea'
            else:
                finishedarea_col = None

            # Price per Square Foot
            if saleprice_col and finishedarea_col:
                df[finishedarea_col] = pd.to_numeric(df[finishedarea_col], errors='coerce')
                df.loc[df[finishedarea_col] <= 0, finishedarea_col] = np.nan  # Avoid division by zero
                df['pricepersqft'] = df[saleprice_col] / df[finishedarea_col]
                df['pricepersqft'].fillna(0, inplace=True)
            else:
                if self.logger:
                    self.logger.warning(
                        "Column 'finishedarea' or 'saleprice' not found. Cannot calculate Price Per Sqft.")
                df['pricepersqft'] = np.nan

            # Map building value column
            if 'building_value' in df.columns:
                buildingvalue_col = 'building_value'
            elif 'buildingvalue' in df.columns:
                buildingvalue_col = 'buildingvalue'
            else:
                buildingvalue_col = None

            # Map land value column
            if 'land_value' in df.columns:
                landvalue_col = 'land_value'
            elif 'landvalue' in df.columns:
                landvalue_col = 'landvalue'
            else:
                landvalue_col = None

            # Land-to-Building Value Ratio
            if buildingvalue_col and landvalue_col:
                df.loc[df[buildingvalue_col] <= 0, buildingvalue_col] = np.nan  # Avoid division by zero
                df['landtobuildingratio'] = df[landvalue_col] / df[buildingvalue_col]
                df['landtobuildingratio'].replace([np.inf, -np.inf], np.nan, inplace=True)
                df['landtobuildingratio'].fillna(df['landtobuildingratio'].median(), inplace=True)
            else:
                df['landtobuildingratio'] = np.nan

            # Sale Price Category
            if saleprice_col:
                df['salepricecategory'] = df[saleprice_col].apply(self.categorize_price)
            else:
                df['salepricecategory'] = 'Unknown'

            # Owner Name Split
            if 'owner_name' in df.columns:
                df['owner_name'].fillna("Unknown Unknown", inplace=True)
                split_names = df['owner_name'].str.split(n=1, expand=True)
                df['ownerfirstname'] = split_names[0]
                df['ownerlastname'] = split_names[1].fillna("")
            else:
                df['ownerfirstname'] = "Unknown"
                df['ownerlastname'] = "Unknown"

            # Is New Construction
            if 'propertyage' in df.columns:
                df['is_new_construction'] = (df['propertyage'] <= 3)
            else:
                df['is_new_construction'] = False

            # Price Outlier Detection
            if saleprice_col:
                price_mean = df[saleprice_col].mean()
                price_std = df[saleprice_col].std()
                upper_bound = price_mean + 2 * price_std
                lower_bound = price_mean - 2 * price_std

                df['price_outlier_status'] = 'Normal'
                df.loc[df[saleprice_col] > upper_bound, 'price_outlier_status'] = 'High Outlier'
                df.loc[df[saleprice_col] < lower_bound, 'price_outlier_status'] = 'Low Outlier'
            else:
                df['price_outlier_status'] = 'Normal'

            # Map tax district column
            if 'tax_district' in df.columns:
                taxdistrict_col = 'tax_district'
            elif 'taxdistrict' in df.columns:
                taxdistrict_col = 'taxdistrict'
            else:
                taxdistrict_col = None

            # Neighborhood Price Index
            if taxdistrict_col and 'pricepersqft' in df.columns:
                neighborhood_avg_price = df.groupby(taxdistrict_col)['pricepersqft'].transform('mean')
                neighborhood_avg_price = neighborhood_avg_price.replace(0, np.nan)
                df['neighborhood_price_ratio'] = df['pricepersqft'] / neighborhood_avg_price
                df['neighborhood_price_index'] = df['neighborhood_price_ratio'].apply(
                    self.categorize_neighborhood_index)
                df['neighborhood_price_index'].fillna("Unknown", inplace=True)
            else:
                df['neighborhood_price_index'] = 'Unknown'
                df['neighborhood_price_ratio'] = np.nan

            # Value Condition Proxy
            if taxdistrict_col and 'pricepersqft' in df.columns and yearbuilt_col:
                df['built_decade'] = (df[yearbuilt_col] // 10) * 10
                decade_neighborhood_avg = df.groupby(['built_decade', taxdistrict_col])['pricepersqft'].transform(
                    'mean')
                decade_neighborhood_avg = decade_neighborhood_avg.replace(0, np.nan)
                df['value_condition_ratio'] = df['pricepersqft'] / decade_neighborhood_avg
                df['value_condition_proxy'] = df['value_condition_ratio'].apply(self.categorize_value_condition)
                df['value_condition_proxy'].fillna("Unknown", inplace=True)
                df.drop(columns=['built_decade'], inplace=True)  # Remove temporary column
            else:
                df['value_condition_proxy'] = 'Unknown'
                df['value_condition_ratio'] = np.nan

            if self.logger:
                self.logger.info("All derived columns added successfully")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error adding derived columns: {str(e)}")

        return df

    def categorize_price(self, price):
        """Categorizes sale price"""
        if pd.isna(price):
            return "Unknown"
        elif price < 100000:
            return "Low"
        elif price <= 300000:
            return "Medium"
        else:
            return "High"

    def categorize_neighborhood_index(self, ratio):
        """Categorizes neighborhood price index"""
        if pd.isna(ratio):
            return "Unknown"
        elif ratio > 1.50:  # > 50% above avg
            return "Significantly Above Average"
        elif ratio > 1.15:  # 15% to 50% above avg
            return "Above Average"
        elif ratio >= 0.85:  # Within +/- 15% of avg
            return "Average"
        elif ratio >= 0.50:  # 15% to 50% below avg
            return "Below Average"
        else:  # More than 50% below avg
            return "Significantly Below Average"

    def categorize_value_condition(self, ratio):
        """Categorizes the value condition proxy"""
        if pd.isna(ratio):
            return "Unknown"
        elif ratio > 1.15:
            return "Above Average for Age/Location"
        elif ratio >= 0.85:
            return "Average for Age/Location"
        else:
            return "Below Average for Age/Location"

    def process(self, df, validation_result=None):
        """Process the Nashville Housing dataset"""
        if self.logger:
            self.logger.info("Starting processing for Nashville Housing dataset")

        # Handle validation results
        if validation_result and not validation_result.get('is_valid', True):
            if self.logger:
                self.logger.warning("Processing data that failed validation")

        # Step 1: Standardize column names
        df = self.standardize_column_names(df)

        # Step 2: Handle missing values in mandatory columns
        df = self.handle_missing_values(df, NASHVILLE_COLUMNS['mandatory_columns'])

        # Step 2.5: Remove duplicate rows
        if self.logger:
            self.logger.info("Removing duplicate rows")
        original_rows = len(df)
        df = df.drop_duplicates()
        removed_duplicates = original_rows - len(df)
        if removed_duplicates > 0:
            if self.logger:
                self.logger.info(f"Removed {removed_duplicates} duplicate rows")

        # Step 3: Remove specified columns
        columns_to_remove = [col.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
                             for col in NASHVILLE_COLUMNS['columns_to_remove']]
        df = self.remove_columns(df, columns_to_remove)

        # Step 4: Type Conversion
        # Convert key columns to appropriate types
        numeric_cols = ['saleprice', 'landvalue', 'buildingvalue', 'totalvalue',
                        'yearbuilt', 'finishedarea', 'acreage', 'bedrooms', 'fullbath', 'halfbath']

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert date columns
        if 'saledate' in df.columns:
            df['saledate'] = pd.to_datetime(df['saledate'], errors='coerce')

        # Step 5: Add derived columns
        df = self.add_derived_columns(df)

        if self.logger:
            self.logger.info(f"Processing completed. Final shape: {df.shape}")

        return df