import logging
import sys
from datetime import datetime
from contextlib import contextmanager


class ColorFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: "\033[36m",    # Cyan
        logging.INFO: "\033[92m",     # Green
        logging.WARNING: "\033[93m",  # Yellow
        logging.ERROR: "\033[91m",    # Red
        logging.CRITICAL: "\033[41m"  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


def setup_logger(logger_name, log_file):
    """Sets up a logger with both file and colorized console output."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console handler (with ANSI colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add both handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_dataframe_info(logger, df, stage_name="Data"):
    logger.info(f"{stage_name} shape: {df.shape}")
    logger.info(f"{stage_name} columns: {list(df.columns)}")
    logger.debug(f"{stage_name} info:\n{df.info()}")
    logger.debug(f"{stage_name} head:\n{df.head()}")


def log_processing_step(logger, step_name, start_time=None):
    if start_time is None:
        logger.info(f"Starting: {step_name}")
        return datetime.now()
    else:
        duration = datetime.now() - start_time
        logger.info(f"Completed: {step_name} (Duration: {duration})")


def log_validation_result(logger, validation_name, is_valid, results):
    if is_valid:
        logger.info(f"{validation_name} - PASSED")
    else:
        logger.error(f"{validation_name} - FAILED")
    if results:
        logger.debug(f"{validation_name} results: {results}")


def log_file_operation(logger, operation, file_path, success):
    status = "Successfully" if success else "Failed to"
    if success:
        logger.info(f"{status} {operation} file: {file_path}")
    else:
        logger.error(f"{status} {operation} file: {file_path}")


@contextmanager
def log_operation_context(logger, operation_name):
    start_time = log_processing_step(logger, operation_name)
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {str(e)}")
        raise
    finally:
        log_processing_step(logger, operation_name, start_time)


def get_logger_context(logger):
    class LoggerContext:
        def __init__(self, operation):
            self._logger = logger
            self.operation = operation
            self.start_time = None

        def __enter__(self):
            self.start_time = log_processing_step(self._logger, self.operation)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                log_exception(self._logger, exc_val, self.operation)
            else:
                log_processing_step(self._logger, self.operation, self.start_time)

    return LoggerContext


def log_exception(logger, exception, context=""):
    if context:
        logger.error(f"Exception in {context}: {str(exception)}")
    else:
        logger.error(f"Exception: {str(exception)}")


