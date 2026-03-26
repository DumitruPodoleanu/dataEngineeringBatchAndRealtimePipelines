# Data Engineering Pipeline - Running Instructions

This README provides instructions for running both batch and real-time processing pipelines.

## General Project Description

This project implements two data engineering pipelines that ingest CSV data, validate data quality, transform records, and write cleaned outputs for analytics and downstream consumption.

### What the Batch Pipeline Does

The batch pipeline processes Nashville housing files from `input/batch/` as a complete dataset run. It validates schema and data integrity (required columns, unrealistic values, duplicates, and date/value consistency), standardizes and cleans columns, creates derived fields (such as `pricepersqft`, `propertyage`, and category/index features), writes processed results to `output/batch/`, and uploads the output to Azure Blob Storage.

### What the Realtime Pipeline Does

The realtime pipeline continuously monitors `input/realtime/` for newly added CSV files and processes each file as it arrives. It performs validation checks (data types, missing values, logical racing constraints, and format checks), applies feature engineering for F1 performance metrics (for example `Points_per_Race`, `Normalized_PPR`, and `Performance_Index`), writes processed files to `output/realtime/`, and uploads them to Azure Blob Storage.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Batch Pipeline

### Using main.py

1. Place your batch file in the input directory:

```bash
cp your_batch_file.csv input/batch/
```

2. Run batch processing only:

```bash
python main.py --mode batch
```

## Running the Real-time Pipeline

1. Start the real-time monitoring:

```bash
python main.py --mode realtime
```

2. Add files to be processed:
   - Place CSV files in `input/realtime/` folder
   - The pipeline will automatically detect and process new files

## Monitoring and Logs

### Log Locations:

- Batch logs: `output/logs/batch_pipeline_*.log`
- Real-time logs: `output/logs/realtime_pipeline_*.log`
- Validation errors: `output/logs/validation_errors_*.log`

### Checking Pipeline Status:

- Batch processing outputs to: `output/batch/`
- Real-time processing outputs to: `output/realtime/`
