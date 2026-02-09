# Data Engineering Pipeline - Running Instructions

This README provides instructions for running both batch and real-time processing pipelines.


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
