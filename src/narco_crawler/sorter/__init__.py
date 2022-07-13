import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
REPORTER_LOG_FILE = "logs/reporter.log"


reporter_logger = logging.getLogger("ingress")
reporter_logger.setLevel(LOG_LEVEL)
reporter_logger_file_handler = FileHandler(REPORTER_LOG_FILE)
reporter_logger_file_handler.setLevel(LOG_LEVEL)
reporter_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
reporter_logger.addHandler(reporter_logger_file_handler)
