import logging as logging

logging.basicConfig(
    level=logging.INFO,
    filename="logs/main.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

try:
    import docker

    client = docker.from_env()
except Exception as e:
    logging.critical("Error with docker client.")
    logging.exception(e, exc_info=True)
    exit()
