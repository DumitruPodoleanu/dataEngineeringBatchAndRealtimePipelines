import pandas as pd

class RealtimeValidator:
    def __init__(self, expected_numeric=None, boolean_columns=None, logger=None):
        self.expected_numeric = expected_numeric or ['Wins', 'Podiums', 'Fastest Laps', 'Poles', 'Points Per Race']
        self.boolean_columns = boolean_columns or ['Active']
        self.logger = logger

    def validate(self, df):
        has_hard_errors = False
        logs = []

        if self.logger:
            self.logger.info("Starting validation...")

        # 1. Duplicates (soft)
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            logs.append(f"Found {duplicate_count} duplicate rows.")
            if self.logger:
                self.logger.warning(logs[-1])

        # 2. Missing values (soft)
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                logs.append(f"Column '{col}' has {count} missing values.")
                if self.logger:
                    self.logger.warning(logs[-1])

        # 3. Non-numeric + Negative values (hard)
        for col in self.expected_numeric:
            if col in df.columns:
                coerced = pd.to_numeric(df[col], errors='coerce')

                non_numeric_count = coerced.isnull().sum()
                if non_numeric_count > 0:
                    has_hard_errors = True
                    logs.append(f"Column '{col}' has {non_numeric_count} non-numeric values.")
                    if self.logger:
                        self.logger.error(logs[-1])

                negative_count = (coerced < 0).sum()
                if negative_count > 0:
                    has_hard_errors = True
                    logs.append(f"Column '{col}' has {negative_count} negative values.")
                    if self.logger:
                        self.logger.error(logs[-1])

        # 4. Boolean columns (hard)
        for col in self.boolean_columns:
            if col in df.columns:
                unique_vals = set(df[col].dropna().unique())
                if not unique_vals.issubset({True, False}):
                    has_hard_errors = True
                    logs.append(f"Column '{col}' has invalid boolean values: {unique_vals}")
                    if self.logger:
                        self.logger.error(logs[-1])

        # 5. Empty strings (soft)
        for col in df.columns:
            if df[col].dtype == object:
                empty_count = (df[col].astype(str).str.strip() == '').sum()
                if empty_count > 0:
                    logs.append(f"Column '{col}' has {empty_count} empty string values.")
                    if self.logger:
                        self.logger.warning(logs[-1])

        # === Data Integrity Rules ===

        # Race_Starts <= Race_Entries (hard)
        if 'Race_Starts' in df.columns and 'Race_Entries' in df.columns:
            count = (df['Race_Starts'] > df['Race_Entries']).sum()
            if count > 0:
                has_hard_errors = True
                logs.append(f"{count} rows where Race_Starts > Race_Entries.")
                if self.logger:
                    self.logger.error(logs[-1])

        # Race_Wins <= Race_Starts (hard)
        if 'Race_Wins' in df.columns and 'Race_Starts' in df.columns:
            count = (df['Race_Wins'] > df['Race_Starts']).sum()
            if count > 0:
                has_hard_errors = True
                logs.append(f"{count} rows where Race_Wins > Race_Starts.")
                if self.logger:
                    self.logger.error(logs[-1])

        # Podiums <= Race_Starts (hard)
        if 'Podiums' in df.columns and 'Race_Starts' in df.columns:
            count = (df['Podiums'] > df['Race_Starts']).sum()
            if count > 0:
                has_hard_errors = True
                logs.append(f"{count} rows where Podiums > Race_Starts.")
                if self.logger:
                    self.logger.error(logs[-1])

        # Decade must be multiple of 10 (soft)
        if 'Decade' in df.columns:
            invalid = (df['Decade'] % 10 != 0).sum()
            if invalid > 0:
                logs.append(f"{invalid} rows have Decade values not a multiple of 10.")
                if self.logger:
                    self.logger.warning(logs[-1])

       # 6. Nationality format with whitelist support (hard)
        allowed_exceptions = {
            "East Germany, West Germany",
            "Rhodesia and Nyasaland",
            "RAF"
        }

        if 'Nationality' in df.columns:
            invalid_nationalities = []

            for val in df['Nationality'].dropna().unique():
                val_stripped = str(val).strip()

                if val_stripped in allowed_exceptions:
                    continue

                # Must contain only alphabetic characters and spaces
                if not all(part.isalpha() or part.isspace() for part in val_stripped):
                    invalid_nationalities.append(val_stripped)
                    continue

                # Must be title case (e.g., "United Kingdom", not "united kingdom")
                if val_stripped != val_stripped.title():
                    invalid_nationalities.append(val_stripped)

            if invalid_nationalities:
                has_hard_errors = True
                logs.append(f"Column 'Nationality' contains invalid format values: {invalid_nationalities}")
                if self.logger:
                    self.logger.error(logs[-1])
            else:
                msg = "Column 'Nationality' contains properly formatted or allowed values."
                if self.logger:
                    self.logger.info(msg)

        if self.logger:
            self.logger.info("Validation complete.")

        return not has_hard_errors, logs