import asyncio

from narco_crawler.config.config import config
from narco_crawler.crawler import crawler_logger as logging
from narco_crawler.engines.ahmia.ahmia import ahmia_main
from narco_crawler.engines.onionland.onionland import onionland_main
from narco_crawler.engines.tordex.tordex import tordex_main


def start_crawler():
    status = True
    logging.info("Starting Crawler.")

    return status


def de_init_crawler():
    status = True
    logging.info("De-initializing Crawler")

    return status


def run_crawler():
    logging.info("Crawler run starting.")

    topics = list(config["keys"].keys())

    for topic in topics:
        asyncio.run(ahmia_main(topic, config["keys"][topic]))
        asyncio.run(tordex_main(topic, config["keys"][topic]))
        asyncio.run(onionland_main(topic, config["keys"][topic]))

    logging.info("Crawler finished.")

    return True
