import logging
import os

def setup_logger(name="voip_analysis_ml", log_file="app.log", level=logging.INFO):
    """
    Sets up a logger with the specified name, log file, and logging level.

    Parameters:
        name (str): Name of the logger.
        log_file (str): File path for the log file.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure log directory exists
    log_directory = os.path.dirname(log_file) if os.path.dirname(log_file) else os.getcwd()
    os.makedirs(log_directory, exist_ok=True)

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler
    file_handler = logging.FileHandler(os.path.join(log_directory, os.path.basename(log_file)))
    file_handler.setLevel(level)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger if they aren't already added
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
