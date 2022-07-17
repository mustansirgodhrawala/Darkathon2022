import logging
import pickle
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
VALIDATOR_LOG_FILE = "logs/validator.log"


validator_logger = logging.getLogger("validator")
validator_logger.setLevel(LOG_LEVEL)
validator_logger_file_handler = FileHandler(VALIDATOR_LOG_FILE)
validator_logger_file_handler.setLevel(LOG_LEVEL)
validator_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
validator_logger.addHandler(validator_logger_file_handler)
import shutup; shutup.please()
try:
	model = pickle.load(open("ml_files/knn.pkl", "rb"))
	validator_logger.info("Successfully loaded model.")
except Exception as e:
	validator_logger.critical("Problem loading model")

try:
	cv = pickle.load(open("ml_files/cv.pickle", "rb"))
	validator_logger.info("Successfully loaded count vectorizer")
except Exception as e:
	validator_logger.critical("Problem loading Count Vectorizer")
