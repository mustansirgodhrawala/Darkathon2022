import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO

# messaging logger
MAIN_LOG_FILE = "logs/main.log"


logging = logging.getLogger("main")
logging.setLevel(LOG_LEVEL)
logging_file_handler = FileHandler(MAIN_LOG_FILE)
logging_file_handler.setLevel(LOG_LEVEL)
logging_file_handler.setFormatter(Formatter(LOG_FORMAT))
logging.addHandler(logging_file_handler)


try:
    import docker

    client = docker.from_env()
except Exception as e:
    logging.critical("Error with docker client.")
    logging.exception(e, exc_info=True)
    exit()
