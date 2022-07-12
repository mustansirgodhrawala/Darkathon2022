import datetime

import mysql.connector
from rich import print as rprint

from narco_crawler.config import config_logger as logging
from narco_crawler.config.config import config


def DatabaseInit(config):
    try:
        logging.info("Starting DB connection.")
        mydb = mysql.connector.connect(
            host=config["database"]["host"],
            user=config["database"]["user"],
            password=config["database"]["pass"],
            database=config["database"]["db"],
        )
        logging.info("Successfully started db connection.")
        return mydb
    except mysql.connector.Error as e:
        if e.errno == 1044:
            logging.critical("Wrong Permissions set on database.")
            rprint("\t\tFailed to connect to database, check logs for more info.")
        else:
            logging.critical("Unknown Exception in database connection.")
            logging.exception(e, exc_info=True)
            rprint("\t\tFailed to connect to database, check logs for more info.")
        exit()
    except KeyError as e:
        logging.critical("Invalid details in config file, cannot connect to database.")
        logging.exception(e, exc_info=True)
        rprint(
            "[red]\t\tBad config file, can't connect to database. Check logs for more details.[/red]"
        )
        exit()


def UpdateDBTime(mydb):
    try:
        logging.info("Updating current access time in db table.")
        cursor = mydb.cursor()
        cursor.execute(
            f'UPDATE operation SET LastUsed="{ str(datetime.datetime.isoformat(datetime.datetime.now())) }" WHERE Id=0'
        )
        mydb.commit()
        logging.info("Successfully updated current access time in db table.")
        return True
    except Exception as e:
        logging.warning("Failed to update current time in database.")
        logging.exception(e, exc_info=True)
        return e


# Initializing Database Connection
database = DatabaseInit(config)
