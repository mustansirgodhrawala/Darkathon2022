import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
INGRESS_LOG_FILE = "logs/ingress.log"


ingress_logger = logging.getLogger("narco_crawler.engines")
ingress_logger.setLevel(LOG_LEVEL)
ingress_logger_file_handler = FileHandler(INGRESS_LOG_FILE)
ingress_logger_file_handler.setLevel(LOG_LEVEL)
ingress_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
ingress_logger.addHandler(ingress_logger_file_handler)
