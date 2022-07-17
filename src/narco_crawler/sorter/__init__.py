import logging
import pickle
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
SORTER_LOG_FILE = "logs/sorter.log"


sorter_logger = logging.getLogger("sorter")
sorter_logger.setLevel(LOG_LEVEL)
sorter_logger_file_handler = FileHandler(SORTER_LOG_FILE)
sorter_logger_file_handler.setLevel(LOG_LEVEL)
sorter_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
sorter_logger.addHandler(sorter_logger_file_handler)

model = pickle.load(open("ml_files/knn.pkl", "rb"))
cv = pickle.load(open("ml_files/cv.pickle", "rb"))
