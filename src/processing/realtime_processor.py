import pandas as pd
import numpy as np


class RealtimeProcessor:
    def __init__(self, logger=None):
        self.logger = logger

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.logger:
            self.logger.info("Starting processing...")

        # 1. Remove duplicate rows
        initial_shape = df.shape
        df = df.drop_duplicates()
        if self.logger:
            removed = initial_shape[0] - df.shape[0]
            self.logger.info(f"Removed {removed} duplicate rows.")

        # 2. Remove rows with missing values
        initial_shape = df.shape
        df = df.dropna()
        if self.logger:
            removed = initial_shape[0] - df.shape[0]
            self.logger.info(f"Removed {removed} rows with missing values.")

        if 'Decade' in df.columns:
            df['Decade'] = (df['Decade'] // 10) * 10
            if self.logger:
                self.logger.info("Normalized Decade values to nearest lower multiple of 10.")

        # 3. Drop unused columns
        drop_cols = ['Championships', 'Champion', 'Fastest Laps']
        for col in drop_cols:
            if col in df.columns:
                df.drop(columns=col, inplace=True)
                if self.logger:
                    self.logger.info(f"Dropped column: {col}")

        # 4. Compute Points per Race
        df['Points_per_Race'] = df['Points'] / df['Race_Entries']
        if self.logger:
            self.logger.info("Calculated Points_per_Race")

        # 5. Normalize PPR by Decade average
        df['Decade_Avg_PPR'] = df.groupby('Decade')['Points_per_Race'].transform('mean')
        df['Normalized_PPR'] = df['Points_per_Race'] / df['Decade_Avg_PPR']
        if self.logger:
            self.logger.info("Normalized Points_per_Race by Decade")

        # 6. Career Length Factor
        df['Career_Length_Factor'] = np.log10(df['Race_Entries'] + 1)
        if self.logger:
            self.logger.info("Calculated Career_Length_Factor using log10")

        # 7. Performance Index
        df['Performance_Index'] = df['Normalized_PPR'] * df['Career_Length_Factor']
        if self.logger:
            self.logger.info("Created Performance_Index")

        # 8. Adjusted Win and Podium Indices
        df['Win_Rate'] = df['Race_Wins'] / df['Race_Entries']
        df['Podium_Rate'] = df['Podiums'] / df['Race_Entries']
        df['Adjusted_Win_Index'] = df['Win_Rate'] * np.log(df['Race_Entries'] + 1)
        df['Adjusted_Podium_Index'] = df['Podium_Rate'] * np.log(df['Race_Entries'] + 1)
        if self.logger:
            self.logger.info("Added Adjusted Win and Podium Indices")

        if self.logger:
            self.logger.info("Processing complete.")

        return df