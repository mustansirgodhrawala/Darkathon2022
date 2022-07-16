import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO


spider_logger = logging.getLogger("spider")
spider_logger.setLevel(LOG_LEVEL)
spider_logger_file_handler = FileHandler("logs/spider.log")
spider_logger_file_handler.setLevel(LOG_LEVEL)
spider_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
spider_logger.addHandler(spider_logger_file_handler)
