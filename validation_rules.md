# Data Engineering Pipeline - Validation Rules Documentation

We separated the validation issues into 2 categories, **SOFT** and **HARD**. The idea is that when getting a soft error, the pipeline does not stop because these errors are fixable in the processing stage, whereas hard errors cause the pipeline to stop because the errors are not fixable in the processing stage.

## Batch Data Processing - Nashville Housing Dataset

### Columns

#### Numeric
- Sale Price
- Land Value
- Building Value
- Total Value
- Acreage
- Year Built
- Bedrooms
- Full Bath
- Half Bath
- Finished Area

#### Date
- Sale Date

#### Categorical
- Parcel ID
- Land Use
- Property Address
- Owner Name
- Owner Address
- Sold As Vacant
- Multiple Parcels Involved in Sale

#### Derived (Calculated)
- Price per Sqft
- Property Age
- Sale Year
- Sale Month
- Land-to-Building Value Ratio
- Sale Price Category
- Owner First Name
- Owner Last Name
- Is New Construction
- Price Outlier Status
- Neighborhood Price Index
- Value Condition Proxy

### Validation Rules

#### General
- **Duplicate Rows**: Checks for exact row duplicates. **SOFT** severity
- **Missing Values**: Checks for missing (Null) values in mandatory columns. **SOFT** severity (handled in processing)

#### Numeric Columns
- **Non-Numeric Values**: Detects values that cannot be converted to numbers. **HARD** severity
- **Negative Values**: Detects negative numbers in Sale Price, Land Value, Building Value, Acreage, Bedrooms, Bathrooms. **HARD** severity
- **Unrealistic Values**: 
  - Sale Price > $10M
  - Bedrooms > 20
  - Full Bath > 10
  - Half Bath > 10
  - Acreage > 1000
  
  **HARD** severity

#### Date Columns
- **Invalid Dates**: Checks for improperly formatted dates. **HARD** severity
- **Future Dates**: Sale Date cannot be in the future. **HARD** severity

#### Data Integrity
- **Year Built Validation**: Year Built must be between 1800 and current year. **HARD** severity
- **Total Value Consistency**: Total Value = Land Value + Building Value (allowing for $1 rounding). **HARD** severity

### Added Columns

#### Derived Columns (Post-processing)
- **Price Per Sqft**: Sale Price / Finished Area
  - Represents the cost per square foot of the property
- **Property Age**: Sale Year - Year Built
  - Age of the property at the time of sale
- **Sale Year and Month**: Extracted from Sale Date
  - Temporal components for time-based analysis
- **Land-to-Building Value Ratio**: Land Value / Building Value
  - Indicates the proportion of land value versus structure value
- **Sale Price Category**: 
  - Low (< $100,000)
  - Medium ($100,000-$300,000) 
  - High (> $300,000)
  - Categorical classification of properties by price range
- **Owner Name Split**: First and Last Name extracted from Owner Name field
  - Separates full name into first and last name components
- **Is New Construction**: Property Age <= 3 years
  - Boolean indicator for recently built properties
- **Price Outlier Status**: 
  - Normal: Within 2 standard deviations of mean sale price
  - High Outlier: More than 2 standard deviations above mean
  - Low Outlier: More than 2 standard deviations below mean
  - Identifies unusually priced properties
- **Neighborhood Price Index**: Based on Tax District
  - Significantly Above Average (> 50% above)
  - Above Average (15-50% above)
  - Average (within ±15%)
  - Below Average (15-50% below)
  - Significantly Below Average (> 50% below)
  - Unknown
  - Price comparison relative to neighborhood average
- **Neighborhood Price Ratio**: Property price per sqft / Neighborhood average price per sqft
  - Quantitative measure of relative property value
- **Value Condition Proxy**: Based on decade of construction and location
  - Above Average for Age/Location
  - Average for Age/Location
  - Below Average for Age/Location
  - Unknown
  - Indicates how property value compares to similar age properties in same area
- **Value Condition Ratio**: Property price per sqft / Decade neighborhood average price per sqft
  - Quantitative measure of value relative to age cohort

### Back-up Validation Rules

#### Post-processing Checks
- **Missing Values**: Derived columns should not contain missing values
- **Negative Values**: Price per Sqft, Property Age, and Ratios must be ≥ 0
- **Range Validation**:
  - Price per Sqft between 0-5000
  - Property Age between 0-300 years
  - Sale Price Category must be "Low", "Medium", or "High"
  - Land-to-Building Ratio > 0
  - Neighborhood Price Ratio > 0
  - Value Condition Ratio > 0

## Real-Time Data Processing - Formula 1 Driver Statistics

We chose to work with a Formula 1 Driver Statistics Dataset for real-time processing.

### Columns

#### Numeric
- Championships
- Race_Entries
- Race_Starts
- Pole_Positions
- Race_Wins
- Podiums
- Fastest_Laps
- Points
- Decade
- Years_Active

#### Boolean
- Active
- Champion

#### Categorical
- Driver
- Nationality

#### Custom (List)
- Seasons (example: [2000, 2001, 2002])

### Validation Rules

#### General
- **Duplicate Rows**: Checks for exact row duplicates. **SOFT** severity
- **Missing Values**: Checks for missing (Null) values in any column. **SOFT** severity

#### Numeric Columns
- **Non-Numeric Values**: Detects values that cannot be converted to numbers. **HARD** severity
- **Negative Values**: Detects negative numbers in all numeric columns. **HARD** severity

#### Boolean Columns
- **Boolean Values**: Checks if values are either True or False. **HARD** severity

#### Categorical Columns
- **Empty Strings**: Checks for string fields that are Empty/Whitespace

#### Data Integrity
- **Race_Starts <= Race_Entries**: Driver cannot start more races than entered. **HARD** severity
- **Race_Wins <= Race_Entries**: Driver cannot win more races than entered. **HARD** severity
- **Podiums <= Race_Starts**: Driver cannot finish on podium more times than started. **HARD** severity
- **Decade % 10 == 0**: Checks if decade is rounded to nearest decade (1980, 1990)
- **Nationality Format**: Must contain only letters and spaces, properly capitalized. 
  
  Allowed exceptions: 
  - "East Germany, West Germany"
  - "Rhodesia and Nyasaland"
  - "RAF"

### Added Columns

#### Derived Columns (Post-processing)
- **Points_per_Race**: Points / Race_Entries
- **Win_Rate**: Race_Wins / Race_Entries
- **Podium_Rate**: Podiums / Race_Entries

### Back-up Validation Rules

#### Post-processing Checks
- **Missing Values**: No post-processed columns should contain missing values
- **Numeric Data Types**: All calculated metrics must maintain numeric data types
- **Negative Values**: No calculated metrics should have negative values
- **Range Checks**:
  - Win_Rate and Podium_Rate must be between 0 and 1
  - Points_per_Race expected between 0 and 100