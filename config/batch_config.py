# config/batch_config.py
import os 

if os.path.exists("/opt/airflow/input/batch"):
    base_input_path = "/opt/airflow/input"
    base_output_path = "/opt/airflow/output"
else:
    base_input_path = "input"
    base_output_path = "output"

# BATCH_CONFIG = {
#     'input_path': '/opt/airflow/input/batch/',
#     'output_path': 'output/batch/nashville_housing_processed.csv',
#     'log_path': 'logs/batch_processing.log',
#     'azure_container': 'housing-data',
#     'azure_blob_name': 'nashville_housing_processed.csv',
#     'remove_columns': [
#         "Image", "Sold As Vacant", "Multiple Parcels Involved in Sale",
#         "Unnamed: 0", "Property Address", "Owner Address"
#     ],
# }

BATCH_CONFIG = {
    'input_path': os.path.join(base_input_path, 'batch'),
    'output_path': os.path.join(base_output_path, 'batch', 'nashville_housing_processed.csv'),
    'log_path': os.path.join(base_output_path, 'logs', 'batch_processing.log'),
    'azure_container': 'housing-data',
    'azure_blob_name': 'nashville_housing_processed.csv',
    'remove_columns': [
        "Image", "Sold As Vacant", "Multiple Parcels Involved in Sale",
        "Unnamed: 0", "Property Address", "Owner Address"
    ],
}