import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
CRAWLER_LOG_FILE = "logs/crawler.log"


crawler_logger = logging.getLogger("crawler")
crawler_logger.setLevel(LOG_LEVEL)
crawler_logger_file_handler = FileHandler(CRAWLER_LOG_FILE)
crawler_logger_file_handler.setLevel(LOG_LEVEL)
crawler_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
crawler_logger.addHandler(crawler_logger_file_handler)
