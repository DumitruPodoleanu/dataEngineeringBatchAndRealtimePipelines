# config/validation_rules.py
NASHVILLE_COLUMNS = {
    'all_columns': [
        'Parcel ID', 'Land Use', 'Property Address', 'Suite/Condo #', 'Property City',
        'Sale Date', 'Sale Price', 'Legal Reference', 'Sold As Vacant',
        'Multiple Parcels Involved in Sale', 'Owner Name', 'Address', 'City', 'State',
        'Tax District', 'Land Value', 'Building Value', 'Total Value', 'Acreage',
        'Year Built', 'Bedrooms', 'Full Bath', 'Half Bath', 'image',
        'Foundation Type', 'Exterior Wall', 'Grade', 'Finished Area',
        'UniqueID', 'Unnamed: 0', 'Neighborhood', 'Unnamed: 0.1'
    ],
    'mandatory_columns': [
        'landuse', 'saleprice', 'legalreference',
        'landvalue', 'buildingvalue', 'totalvalue',
        'yearbuilt', 'bedrooms', 'fullbath', 'halfbath', 'saledate', 'finishedarea',
        'acreage', 'parcelid', 'uniqueid'
    ],
    'non_mandatory_columns': [
        "Suite/Condo", "Owner Name", "Address", "City", "State",
        "Tax District", "Image", "Foundation Type", "Exterior Wall", "Grade",
        "Unnamed: 0", "Property Address", "Owner Address"
    ],
    'columns_to_remove': [
        "Image", "Sold As Vacant", "Multiple Parcels Involved in Sale",
        "Unnamed: 0", "Property Address", "Owner Address"
    ],
    'derived_columns': [
        'pricepersqft',
        'propertyage',
        'saleyear',
        'salemonth',
        'landtobuildingratio',
        'salepricecategory',
        'ownerfirstname',
        'ownerlastname',
        'is_new_construction',
        'price_outlier_status',
        'neighborhood_price_index',
        'value_condition_proxy'
    ],
    'validation_rules': {
        'parcelid': {
            'nullable': False,
            'datatype': str,
            'pattern': r'^[0-9A-Z\-]+$',  # Alphanumeric with dashes
            'min_length': 3,
            'max_length': 50
        },
        'landuse': {
            'nullable': False,
            'datatype': str,
            'valid_values': [
                'VACANT RESIENTIAL LAND',
                'SINGLE FAMILY',
                'MOBILE HOME',
                'DUPLEX',
                'TRIPLEX',
                'FOURPLEX',
                'SPLIT CLASS',
                'RESIDENTIAL CONDO',
                'ROOMING HOUSE',
                'RESIDENTIAL COMBO/MISC',
                'VACANT RURAL LAND',
                'FARM',
                'ESTATE',
                'VACANT INDUSTRIAL',
                'WAREHOUSE',
                'VACANT COMMERCIAL',
                'OFFICE BUILDING'
            ]
        },
        'saleprice': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 10000000,  # $10M max
            'exclude_negative': True
        },
        'saledate': {
            'nullable': False,
            'datatype': 'datetime',
            'future_dates': False,
            'min_year': 1900
        },
        'yearbuilt': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 1800,
            'max_value': 2025,
            'exclude_future': True
        },
        'bedrooms': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 20
        },
        'fullbath': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 10
        },
        'halfbath': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 10
        },
        'acreage': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 1000
        },
        'landvalue': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 10000000
        },
        'buildingvalue': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 10000000
        },
        'totalvalue': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 0,
            'max_value': 20000000,
            'relationship': lambda row: abs(row['totalvalue'] - (row['landvalue'] + row['buildingvalue'])) <= 1
        },
        'finishedarea': {
            'nullable': False,
            'datatype': (int, float),
            'min_value': 100,  # min square footage for a house
            'max_value': 50000
        }
    },
    'cross_field_validations': [
        {
            'name': 'Total Value Consistency',
            'description': 'Total Value = Land Value + Building Value',
            'validate': lambda row: abs(row['totalvalue'] - (row['landvalue'] + row['buildingvalue'])) <= 1
        },
        {
            'name': 'Price Per Sqft Sanity Check',
            'description': 'Sale Price / Finished Area should be reasonable',
            'validate': lambda row: 1 <= (row['saleprice'] / row['finishedarea']) <= 5000
        },
        {
            'name': 'Age Consistency',
            'description': 'Property age should be positive',
            'validate': lambda row: (row['saleyear'] - row['yearbuilt']) >= 0
        }
    ]
}