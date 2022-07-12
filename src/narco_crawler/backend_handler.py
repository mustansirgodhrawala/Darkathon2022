import datetime
import time

import docker
import kafka
import requests
from alive_progress import alive_bar
from kafka import KafkaProducer
from rich import print as rprint

from narco_crawler import client
from narco_crawler import logging
from narco_crawler.db import database
from narco_crawler.db import UpdateDBTime


class Docker_Images:
    Load_Balancer = "./src/narco_crawler/narco_infra/loadbalancer"
    Tor_Proxy = "./src/narco_crawler/narco_infra/tor"


def db_init():
    try:
        logging.info("Loading previous runtime from database.")
        cursor = database.cursor()
        cursor.execute("SELECT LastUsed from operation")
        lastused = cursor.fetchall()
        diff = datetime.datetime.now() - datetime.datetime.fromisoformat(lastused[0][0])
        rprint(
            f"\n\t\t[green]Script Last Runtime: { int(diff.seconds/60) }minutes ago.[/green]"
        )
        logging.info("Successfully loaded previous runtime from database.")
    except Exception as e:
        logging.warning(
            "Failed to load previous runtime from database, this will make it difficult to time newer functions."
        )
        logging.exception(e, exc_info=True)
        return False

    # Setting New Runtime To DB
    status = UpdateDBTime(database)

    return status


def infra_init(build):
    def build_images():
        try:
            logging.info("Starting build of docker images.")
            client.images.build(path=Docker_Images.Tor_Proxy, tag="tor_proxy")
            client.images.build(path=Docker_Images.Load_Balancer, tag="load_balancer")
            logging.info("Finished build of docker images.")
            return True
        except Exception as e:
            logging.critical("Failed build of docker images.")
            logging.exception(e, exc_info=True)
            return False

    def torone():
        status = True

        try:
            data = client.containers.get("torone")
        except (requests.exceptions.HTTPError, docker.errors.NotFound):
            data = None

        # TORDEX Proxy Container
        try:
            if not data:
                logging.info("Starting torone docker containers")
                client.containers.run(
                    "tor_proxy",
                    detach=True,
                    name="torone",
                    network="narco_crawler",
                    remove=True,
                )
                logging.info("Started torone docker containers")
            else:
                logging.warning(
                    "Existing torone container exists, please don't force stop application"
                )
                return "pre-existing"
        except Exception as e:
            logging.critical("Failed starting torone docker containers")
            logging.exception(e, exc_info=True)
            status = False

        return status

    def load_balancer():
        status = True

        try:
            data = client.containers.get("balancer_container")
        except (requests.exceptions.HTTPError, docker.errors.NotFound):
            data = None

        # TORDEX Load Balancer
        try:
            if not data:
                logging.info("Starting Load Balancer Docker Containers")
                client.containers.run(
                    "load_balancer",
                    detach=True,
                    name="balancer_container",
                    network="narco_crawler",
                    remove=True,
                    ports={"9050/tcp/udp": 9050},
                )
                logging.info("Started Load Balancer Docker Containers")
            else:
                logging.warning(
                    "Existing Load Balancer container exists, please don't force stop application"
                )
                return "pre-existing"
        except Exception as e:
            logging.critical("Failed Load Balancer Docker Containers")
            logging.exception(e, exc_info=True)
            status = False

        return status

    status = True

    # Start building Backend Infra
    if build:
        status = build_images()
    else:
        logging.info("Not building docker images(user input).")

    # Start containers
    status_torone = torone()
    status_load_balancer = load_balancer()
    if status_torone == "pre-existing" and status_load_balancer == "pre-existing":
        pass
    elif not status_torone or not status_load_balancer:
        return False
    elif status_torone and status_load_balancer:
        rprint("\t\t[green]Waiting for backend to setup.")
        with alive_bar(10) as bar:
            bar.title = "\t\tBackend starting...."
            for _ in range(10):
                time.sleep(1)
                bar()

    return status


def kafka_init():
    try:
        logging.info("Testing Kafka Availability")
        KafkaProducer(bootstrap_servers="localhost:9092")
        return True
    except kafka.errors.NoBrokersAvailable:
        logging.critical("Kafka Unavailable")
        return False
    except Exception as e:
        logging.critical("Exception generated when trying to test kafka config.")
        logging.exception(e, exc_info=True)
        return False


def initializer(build=False):

    status = True

    status = db_init()
    if not infra_init(build):
        status = False

    if not kafka_init():
        status = False

    return status


def de_initializer():
    try:
        logging.info("Stopping running docker containers.")
        # Getting containers by their name and stopping them, using docker sdk.
        client.containers.get("torone").stop()
        client.containers.get("balancer_container").stop()
        logging.info("Stopped running docker containers.")
        return True
    except Exception as e:
        logging.warning("Failed to stop running docker containers.")
        logging.exception(e, exc_info=True)
        return False


def backend_tester():
    logging.info("Checking if backend infrastructure is working.")
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050",
    }
    try:
        requests.get(
            "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/",
            proxies=proxies,
            timeout=10,
        )
        logging.info("Backend infrastructure is working.")
        return True
    except Exception:
        try:
            logging.warning("Backend has failed Test 1.")
            requests.get(
                "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/",
                proxies=proxies,
                timeout=30,
            )
            logging.info("Backend infrastructure is working.")
            return True
        except Exception as e:
            logging.critical("Backend has failed Test 2.")
            logging.exception(e, exc_info=True)
            return False
