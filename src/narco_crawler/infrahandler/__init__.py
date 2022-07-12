import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
INFRA_LOG_FILE = "logs/infra.log"


infra_logger = logging.getLogger("infrahandler")
infra_logger.setLevel(LOG_LEVEL)
infra_logger_file_handler = FileHandler(INFRA_LOG_FILE)
infra_logger_file_handler.setLevel(LOG_LEVEL)
infra_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
infra_logger.addHandler(infra_logger_file_handler)
