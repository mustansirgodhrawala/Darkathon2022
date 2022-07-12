import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
ENGINES_LOG_FILE = "logs/engines.log"


engines_logger = logging.getLogger("narco_crawler.engines")
engines_logger.setLevel(LOG_LEVEL)
engines_logger_file_handler = FileHandler(ENGINES_LOG_FILE)
engines_logger_file_handler.setLevel(LOG_LEVEL)
engines_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
engines_logger.addHandler(engines_logger_file_handler)
