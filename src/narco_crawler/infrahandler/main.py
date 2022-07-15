import datetime
import time

import docker
import kafka
import requests
from alive_progress import alive_bar
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic
from rich import print as rprint

from narco_crawler import client
from narco_crawler import logging as mainlog
from narco_crawler.infrahandler import infra_logger as logging

logging.info("Logger for InfraHandler Created.")
from narco_crawler.config.db import database
from narco_crawler.config.db import UpdateDBTime
from narco_crawler.config.config import config
import mysql.connector


def add_schema(config):
    logging.info("Creating database schema.")

    mycursor = database.cursor()
    topics = list(config["keys"].keys())
    topics.append("markets")
    for topic in topics:
        try:
            mycursor.execute(f"CREATE TABLE {topic}_ingress (links varchar(1000))")
        except mysql.connector.Error as e:
            if e.errno == 1050:
                mycursor.execute(f"TRUNCATE TABLE {topic}_ingress")
                logging.info("Just needed to truncate, table already existed.")
                logging.warning(
                    "This means application was halted during execution and infra was not de-initialized."
                )
            else:
                logging.critical(
                    f"Failed to create database schema for {topic}, it's a mysql error"
                )
                logging.exception(e, exc_info=True)
                return False
        except Exception as e:
            logging.critical(f"Failed to create database schema for {topic}.")
            logging.exception(e, exc_info=True)
            return False
        finally:
            database.commit()

    logging.info("Created database schema.")
    return True


def delete_schema(config):
    logging.info("Deleted database schema.")
    mycursor = database.cursor()
    topics = list(config["keys"].keys())
    for topic in topics:
        try:
            mycursor.execute(f"DROP TABLE {topic}_ingress")
        except mysql.connector.Error as e:
            if e.errno == 1051:
                logging.critical(
                    "Table does not exist, this is abnormal. Please report."
                )
            else:
                logging.critical("MYSQL Error exists.")
                logging.exception(e, exc_info=True)
        except Exception as e:
            logging.warning("Failed to delete database tables.")
            logging.exception(e, exc_info=True)
            return False
    database.commit()
    logging.info("Deleted database schema.")
    return True


def docker_infra_restart():
    def restart_torone():
        logging.info("Restarting torone docker containers")
        client.containers.get("torone").restart()
        client.containers.get("tortwo").restart()
        logging.info("Restarting torone docker containers")

    def load_balancer():
        logging.info("Restarting Load Balancer containers")
        client.containers.get("balancer_container").restart()
        logging.info("Restarting Load Balancer containers")

    rprint("\t\t[green]Waiting for backend to restart.")
    with alive_bar(20) as bar:
        bar.title = "\t\tBackend restarting...."
        for _ in range(20):
            time.sleep(1)
            bar()
    return True


class Docker_Images:
    Load_Balancer = "./src/narco_crawler/backend/loadbalancer"
    Tor_Proxy = "./src/narco_crawler/backend/tor"


def create_topics_kafka(topics):
    topics.append("markets")
    logging.info("Creating kafka topics")
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers="localhost:9092", client_id="test"
        )
        logging.info("Created kafka admin_client")
    except Exception as e:
        logging.critical(
            "Error when trying to create admin client object, kafka topic creation."
        )
        logging.exception(e, exc_info=True)
        return False

    try:
        admin_client.delete_topics(topics)
    except Exception:
        pass

    # Make topics list
    topic_list = []
    for topic in topics:
        topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=1))

    # Actually creating topics
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
    except kafka.errors.TopicAlreadyExistsError:
        pass
    except Exception as e:
        logging.critical("Exception when creating kafka topics.")
        logging.exception(e, exc_info=True)
        return False
    finally:
        logging.info("Successfully created kafka topics.")
        return True


def delete_topics_kafka(topics):
    topics.append("markets")
    logging.info("Deleting kafka topics")
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers="localhost:9092", client_id="test"
        )
        logging.info("Created kafka admin_client")
    except Exception as e:
        logging.critical(
            "Error when trying to create admin client object, kafka topic creation."
        )
        logging.exception(e, exc_info=True)
        return False

    try:
        admin_client.delete_topics(topics)
    except Exception as e:
        logging.critical("Exception when deleting kafka topics.")
        logging.exception(e, exc_info=True)
        return False
    finally:
        logging.info("Successfully deleted kafka topics.")
        return True


def db_init():
    try:
        logging.info("Loading previous runtime from database.")
        cursor = database.cursor()
        cursor.execute("SELECT LastUsed from operation")
        lastused = cursor.fetchall()
        diff = datetime.datetime.now() - datetime.datetime.fromisoformat(lastused[0][0])
        rprint(
            f"\t\t[green]Script Last Runtime: { int(diff.seconds/60) }minutes ago.[/green]"
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


def infra_init(build, rebuild=False):
    def build_images():
        try:
            logging.info("Starting build of docker images.")
            client.images.build(path=Docker_Images.Tor_Proxy, tag="tor_proxy")
            client.images.build(path=Docker_Images.Load_Balancer, tag="load_balancer")
            logging.info("Finished build of docker images.")
            return True
        except TypeError:
            logging.critical(
                "Directory supplied to backend infra is invalid, please fix inside configuration files."
            )
            mainlog.critical(
                "Directory supplied to backend infra is invalid(building failed), please fix inside configuration files."
            )
        except Exception as e:
            logging.critical("Failed build of docker images.")
            logging.exception(e, exc_info=True)
            return False

    def torone():
        status = True

        try:
            data = client.containers.get("torone")
            data = client.containers.get("tortwo")
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
                    environment=["TOR_INSTANCES=30"],
                )
                client.containers.run(
                    "tor_proxy",
                    detach=True,
                    name="tortwo",
                    network="narco_crawler",
                    remove=True,
                    environment=["TOR_INSTANCES=30"],
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
                    ports={"9050/tcp": 9050, "9050/udp": 9050},
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
        with alive_bar(15) as bar:
            bar.title = "\t\tBackend starting...."
            for _ in range(15):
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


def backend_test_starter(skip_test):
    if skip_test is False:
        if backend_tester():
            rprint("\t\t[green]Backend infrastructure is functional[/green]")
            logging.info("Backend Test Successfull")
            return True
        else:
            rprint(
                "\t\t[red]Backend infrastructure has failed testing, check logs for more details.[/red]"
            )
            logging.warning("Backend Test Failed, check logs for more info")
            return False


def initializer(build, skip_test=False):
    logging.info("Starting infrastructure.")
    status = True

    status = db_init()
    if not infra_init(build):
        status = False

    if not backend_test_starter(skip_test):
        return False

    if not kafka_init():
        status = False

    if not add_schema(config):
        status = False

    if not create_topics_kafka(list(config["keys"].keys())):
        status = False

    return status


def infra_de_init():
    try:
        logging.info("Stopping running docker containers.")

        # Getting containers by their name and stopping them, using docker sdk.
        client.containers.get("torone").stop()
        client.containers.get("tortwo").stop()
        client.containers.get("balancer_container").stop()
        logging.info("Stopped running docker containers.")
        return True
    except Exception as e:
        logging.info("Failed to stop running docker containers.")
        logging.exception(e, exc_info=True)
        return False


def de_initializer():
    try:
        logging.info("Stopping infrastructure.")
        status = True

        if not infra_de_init():
            status = False

        if not delete_topics_kafka(list(config["keys"].keys())):
            status = False

        if not delete_schema(config):
            status = False

        if status is True:
            logging.info("Successfully stopped infrastructure.")

        return status

    except Exception as e:
        logging.warning("Failed to stop infrastructure, exception occured.")
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
            "facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion",
            proxies=proxies,
            timeout=30,
        )
        logging.info("Backend infrastructure is working.")
        return True
    except Exception:
        try:
            logging.warning("Backend has failed Test 1.")
            time.sleep(5)
            requests.get(
                "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion",
                proxies=proxies,
                timeout=45,
            )
            logging.info("Backend infrastructure is working.")
            return True
        except Exception:
            logging.warning("Backend has failed Test 2.")
            logging.warning("Restarting docker infrastructure")
            if docker_infra_restart():
                logging.info("Restarted Backend Docker Infrastructure.")
                try:
                    requests.get(
                        "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion",
                        proxies=proxies,
                        timeout=60,
                    )
                    logging.info("Backend infrastructure is working.")
                    return True
                except Exception as e:
                    logging.warning("Backend has failed Test 3.")
                    logging.critical("Exception occured when trying test 3.")
                    logging.exception(e, exc_info=True)
            else:
                logging.critical("Failed to restart backend docker infrastructure.")
