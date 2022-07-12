import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
CONFIG_LOG_FILE = "logs/config.log"


config_logger = logging.getLogger("main")
config_logger.setLevel(LOG_LEVEL)
config_logger_file_handler = FileHandler(CONFIG_LOG_FILE)
config_logger_file_handler.setLevel(LOG_LEVEL)
config_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
config_logger.addHandler(config_logger_file_handler)
