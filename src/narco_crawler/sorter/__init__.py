import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO


sorter_logger = logging.getLogger("sorter")
sorter_logger.setLevel(LOG_LEVEL)
sorter_logger_file_handler = FileHandler("logs/sorter.log")
sorter_logger_file_handler.setLevel(LOG_LEVEL)
sorter_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
sorter_logger.addHandler(sorter_logger_file_handler)
