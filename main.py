import os
import time
from datetime import datetime
import argparse
import glob

from config.batch_config import BATCH_CONFIG
from src.processing.realtime_processor import RealtimeProcessor
from src.processing.batch_processor import BatchProcessor
from src.utils.logging_utils import (
    setup_logger,
    log_dataframe_info,
    log_processing_step,
    log_validation_result,
    log_file_operation,
    get_logger_context,
    log_exception
)
from src.data_io.reader import Reader
from src.data_io.writer import Writer
from src.validation.realtime_validator import RealtimeValidator
from src.validation.realtime_backup_validator import RealtimeBackupValidator
from src.validation.batch_validator import BatchValidator
from src.validation.batch_backup_validator import BatchBackupValidator
from src.data_io.azure_connector import upload_to_blob_storage

class DataPipelineManager:
    def __init__(self):
        os.makedirs("output/realtime", exist_ok=True)
        os.makedirs("output/batch", exist_ok=True)
        os.makedirs("output/logs", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.realtime_logger = setup_logger(
            "realtime_pipeline",
            f"output/logs/realtime_pipeline_{timestamp}.log"
        )
        self.batch_logger = setup_logger(
            "batch_pipeline",
            f"output/logs/batch_pipeline_{timestamp}.log"
        )

    def run_batch_processing(self):

        with get_logger_context(self.batch_logger)("Batch Processing Mode"):
            input_path = BATCH_CONFIG.get("input_path")

            if not os.path.isdir(input_path):
                self.batch_logger.error(f"Batch input path does not exist: {input_path}")
                return

            files = glob.glob(os.path.join(input_path, "*"))
            valid_files = [f for f in files if f.endswith((".csv", ".xlsx", ".xls"))]

            if not valid_files:
                self.batch_logger.info("No valid batch files found to process.")
                return

            for file_path in valid_files:
                self.process_batch_file(file_path)

    def process_realtime_file(self, file_path):
        self.realtime_logger.info(f"Processing realtime file: {file_path}")

        try:
            start_time = log_processing_step(self.realtime_logger, "Reading Realtime File")
            reader = Reader(logger=self.realtime_logger)
            df = reader.read(file_path)
            log_processing_step(self.realtime_logger, "Reading Realtime File", start_time)

            if df is None:
                log_file_operation(self.realtime_logger, "Read", file_path, success=False)
                return False

            log_file_operation(self.realtime_logger, "Read", file_path, success=True)
            log_dataframe_info(self.realtime_logger, df, "Initial Realtime Data")

            start_time = log_processing_step(self.realtime_logger, "Realtime Validation")
            validator = RealtimeValidator(logger=self.realtime_logger)
            is_valid, logs = validator.validate(df)
            log_processing_step(self.realtime_logger, "Realtime Validation", start_time)

            for log in logs:
                self.realtime_logger.info(log)

            if not is_valid:
                self.realtime_logger.error("Initial validation failed. Logging issues to file.")
                return False

            start_time = log_processing_step(self.realtime_logger, "Realtime Processing")
            processor = RealtimeProcessor(logger=self.realtime_logger)
            processed_df = processor.process(df)
            log_processing_step(self.realtime_logger, "Realtime Processing", start_time)

            log_dataframe_info(self.realtime_logger, processed_df, "Processed Realtime Data")

            start_time = log_processing_step(self.realtime_logger, "Backup Validation")
            backup_validator = RealtimeBackupValidator(logger=self.realtime_logger)
            post_valid, post_logs = backup_validator.validate(processed_df)
            log_processing_step(self.realtime_logger, "Backup Validation", start_time)

            for log in post_logs:
                self.realtime_logger.info(log)

            if not post_valid:
                self.realtime_logger.error("Post-processing validation failed.")
                return False

            start_time = log_processing_step(self.realtime_logger, "Writing Realtime Output")
            writer = Writer(logger=self.realtime_logger)
            output_path = os.path.join("output/realtime", os.path.basename(file_path))
            success = writer.write(processed_df, output_path)
            log_processing_step(self.realtime_logger, "Writing Realtime Output", start_time)

            log_file_operation(self.realtime_logger, "Write", output_path, success)

            if success:
                blob_name = os.path.basename(output_path)
                container_name = "real-time"
                upload_success, message = upload_to_blob_storage(output_path, container_name, blob_name)

                if upload_success:
                    self.realtime_logger.info(message)
                else:
                    self.realtime_logger.error(message)

            return success

        except Exception as e:
            log_exception(self.realtime_logger, e, f"processing realtime file {file_path}")
            return False

    def process_batch_file(self, file_path):
        self.batch_logger.info(f"Processing batch file: {file_path}")

        try:
            start_time = log_processing_step(self.batch_logger, "Reading Batch File")
            reader = Reader(logger=self.batch_logger)
            df = reader.read(file_path)
            log_processing_step(self.batch_logger, "Reading Batch File", start_time)

            if df is None:
                log_file_operation(self.batch_logger, "Read", file_path, success=False)
                return False

            log_file_operation(self.batch_logger, "Read", file_path, success=True)
            log_dataframe_info(self.batch_logger, df, "Initial Batch Data")

            start_time = log_processing_step(self.batch_logger, "Batch Validation")
            validator = BatchValidator(logger=self.batch_logger)
            is_valid, validation_results = validator.validate(df)
            log_processing_step(self.batch_logger, "Batch Validation", start_time)

            log_validation_result(self.batch_logger, "Batch Validation", is_valid, validation_results)

            if not is_valid:
                self.batch_logger.error("Initial validation failed. Logging issues to file.")
                return False

            start_time = log_processing_step(self.batch_logger, "Batch Processing")
            processor = BatchProcessor(logger=self.batch_logger)
            processed_df = processor.process(df, validation_results)
            log_processing_step(self.batch_logger, "Batch Processing", start_time)

            log_dataframe_info(self.batch_logger, processed_df, "Processed Batch Data")

            start_time = log_processing_step(self.batch_logger, "Backup Validation")
            backup_validator = BatchBackupValidator(logger=self.batch_logger)
            post_valid, post_logs = backup_validator.validate(processed_df)
            log_processing_step(self.batch_logger, "Backup Validation", start_time)

            for log in post_logs:
                self.batch_logger.info(log)

            if not post_valid:
                self.batch_logger.error("Post-processing validation failed.")
                return False

            start_time = log_processing_step(self.batch_logger, "Writing Batch Output")
            writer = Writer(logger=self.batch_logger)
            output_path = os.path.join("output/batch", os.path.basename(file_path))
            success = writer.write(processed_df, output_path)
            log_processing_step(self.batch_logger, "Writing Batch Output", start_time)

            log_file_operation(self.batch_logger, "Write", output_path, success)

            if success:
                blob_name = os.path.basename(output_path)
                container_name = "batch"
                upload_success, message = upload_to_blob_storage(output_path, container_name, blob_name)

                if upload_success:
                    self.batch_logger.info(message)
                else:
                    self.batch_logger.error(message)

            return success

        except Exception as e:
            log_exception(self.batch_logger, e, f"processing batch file {file_path}")
            return False

    def run_realtime_monitoring(self):
        with get_logger_context(self.realtime_logger)("Realtime Monitoring Mode"):
            input_folder = "input/realtime"
            if not os.path.exists(input_folder):
                self.realtime_logger.error(f"Input folder '{input_folder}' does not exist.")
                return

            already_seen = set(os.listdir(input_folder))
            self.realtime_logger.info("Watching for new files...")

            try:
                while True:
                    current_files = set(os.listdir(input_folder))
                    new_files = current_files - already_seen

                    for file_name in new_files:
                        if file_name.endswith(".csv"):
                            file_path = os.path.join(input_folder, file_name)
                            self.process_realtime_file(file_path)

                    already_seen = current_files
                    time.sleep(5)

            except KeyboardInterrupt:
                self.realtime_logger.info("Stopping realtime monitoring")


def main():
    parser = argparse.ArgumentParser(description='Run data engineering pipeline')
    parser.add_argument('--mode', choices=['batch', 'real-time'], default='real-time', help='Pipeline mode')
    args = parser.parse_args()

    pipeline_manager = DataPipelineManager()

    if args.mode == 'real-time':
        pipeline_manager.run_realtime_monitoring()

    elif args.mode == 'batch':
        input_dir = BATCH_CONFIG.get("input_path")

        # DEBUG PRINTS to help with path issues
        print(f"Looking for batch files in: {input_dir}")
        if os.path.isdir(input_dir):
            print("Directory found. Files inside:")
            print(os.listdir(input_dir))
        else:
            print("❌ Directory not found.")

        if os.path.isdir(input_dir):
            pipeline_manager.run_batch_processing()
        else:
            print(f"Invalid batch input path: {input_dir}")

    
    # elif args.mode == 'batch':
    #     input_dir = BATCH_CONFIG.get("input_path")
    #     if os.path.isdir(input_dir):
    #         pipeline_manager.run_batch_processing()
    #         # files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith((".csv", ".xlsx", ".xls"))]
    #         # if not files:
    #         #     print("No valid batch files found.")
    #         # for file_path in files:
    #         #     pipeline_manager.process_batch_file(file_path)
    #     else:
    #         print("Invalid batch input path.")

if __name__ == "__main__":
    main()
