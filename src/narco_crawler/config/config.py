import json
import os

from rich import print as rprint

from narco_crawler.config import config_logger as logging


def ImportConfig(config_file):
    try:
        with open(config_file) as f:
            config = json.load(f)
        logging.info("Successfully loaded config file.")
        return config
    except FileNotFoundError:
        logging.critical("CONFIG FILE DOES NOT EXIST. TERMINATING NOW.")
        rprint("[red]Log file not found, terminating now. Check logs for more info.")
        exit()
    except Exception as e:
        logging.critical("Exception caused during loading config file.")
        logging.exception(e, exc_info=True)
        rprint(
            "[red]Error while loading config file, check logs for more details.[/red]"
        )
        exit()


# Config Init
logging.info("Loading config file from env variable.")
try:
    file = os.environ.get("config_file")
    if file is None:
        logging.critical(
            'log file variable is not set in env. Set "config_file" as env variable with file path'
        )
        rprint(
            "\t\t[red]Log file variable is not set in environment. Check documentation for info on env variables.[/red]"
        )
        exit()
    else:
        config = ImportConfig(str(file))
except Exception as e:
    logging.critical("Exception when loading config. Check logs for more details.")
    rprint("\t\t[red]Exception when loading config. Check logs for more details.[/red]")
    logging.exception(e, exc_info=True)
    exit()


def maxcores():
    try:
        max = config["max_process_count"][0]
        if max:
            logging.info(f"Returning max count as { max }")
            return int(max)
    except Exception:
        logging.info(f"Max count not found in config providing: { os.cpu_count() - 1 }")
        return os.cpu_count() - 1
