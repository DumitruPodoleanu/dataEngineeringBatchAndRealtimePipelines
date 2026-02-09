import pandas as pd

class RealtimeBackupValidator:

    def __init__(self, columns_to_check=None, logger=None):
        self.columns_to_check = columns_to_check or [
            "Points_per_Race", "Decade_Avg_PPR", "Normalized_PPR",
            "Career_Length_Factor", "Performance_Index",
            "Win_Rate", "Podium_Rate", "Adjusted_Win_Index", "Adjusted_Podium_Index"
        ]
        self.logger = logger

    def validate(self, df):
        issues_found = False
        logs = []

        if self.logger:
            self.logger.info("Starting backup validation for processed columns...")

        for col in self.columns_to_check:
            if col not in df.columns:
                message = f"Missing expected column: '{col}'"
                logs.append(message)
                if self.logger: self.logger.error(message)
                issues_found = True
                continue

            if df[col].isnull().any():
                message = f"Column '{col}' has missing values."
                logs.append(message)
                if self.logger: self.logger.warning(message)
                issues_found = True

            if not pd.api.types.is_numeric_dtype(df[col]):
                message = f"Column '{col}' is not numeric."
                logs.append(message)
                if self.logger: self.logger.error(message)
                issues_found = True

            if (df[col] < 0).any():
                message = f"Column '{col}' has negative values."
                logs.append(message)
                if self.logger: self.logger.warning(message)
                issues_found = True

            if col in ["Win_Rate", "Podium_Rate"]:
                if (df[col] > 1).any():
                    message = f"Column '{col}' has values greater than 1."
                    logs.append(message)
                    if self.logger: self.logger.warning(message)
                    issues_found = True

            # Additional rule: Points_per_Race range
            if col == "Points_per_Race":
                if (df[col] < 0).any() or (df[col] > 100).any():
                    message = f"Column '{col}' has values outside expected range (0-100)."
                    logs.append(message)
                    if self.logger: self.logger.warning(message)
                    issues_found = True

            # Career_Length_Factor expected to be in a reasonable range
            if col == "Career_Length_Factor":
                if (df[col] <= 0).any() or (df[col] > 3).any():
                    message = f"Column '{col}' has values outside expected range (0-3)."
                    logs.append(message)
                    if self.logger: self.logger.warning(message)
                    issues_found = True

            # Performance_Index should be positive
            if col == "Performance_Index":
                if (df[col] < 0).any():
                    message = f"Column '{col}' has zero or negative values."
                    logs.append(message)
                    if self.logger: self.logger.warning(message)
                    issues_found = True

        if not issues_found:
            message = "Post-Processing Validation Complete."
            logs.append(message)
            if self.logger: self.logger.info(message)

        return not issues_found, logs