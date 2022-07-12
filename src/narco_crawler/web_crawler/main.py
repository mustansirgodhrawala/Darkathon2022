import asyncio

import kafka
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic

from narco_crawler import logging
from narco_crawler.config import config
from narco_crawler.engines.ahmia.ahmia import ahmia_main
from narco_crawler.engines.tordex.tordex import tordex_main


def create_topics(topics):
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


def delete_topics(topics):
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


def start_crawler():
    logging.info("Starting Crawler.")

    # Creating kafka topics
    topics = list(config["keys"].keys())
    status = create_topics(topics)

    return status


def de_init_crawler():
    logging.info("De-initializing Crawler")

    # Creating kafka topics list
    topics = list(config["keys"].keys())
    status = delete_topics(topics)

    return status


def run_crawler():
    logging.info("Crawler run starting.")

    topics = list(config["keys"].keys())

    for topic in topics:
        asyncio.run(ahmia_main(topic, config["keys"][topic]))
        asyncio.run(tordex_main(topic, config["keys"][topic]))

    logging.info("Crawler finished.")

    return True
