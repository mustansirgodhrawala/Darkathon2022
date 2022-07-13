import asyncio
import multiprocessing

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


def ahmia(topic, keywords):
    asyncio.run(ahmia_main(topic, config["keys"][topic]))


def tordex(topic, keywords):
    asyncio.run(tordex_main(topic, config["keys"][topic]))


def onionland(topic, keywords):
    asyncio.run(onionland_main(topic, config["keys"][topic]))


def run_crawler():
    logging.info("Crawler run starting.")

    topics = list(config["keys"].keys())

    processes = []

    for topic in topics:
        p = multiprocessing.Process(target=ahmia, args=(topic, config["keys"][topic]))
        processes.append(p)
        # p = multiprocessing.Process(target=tordex, args=(topic, config["keys"][topic]))
        # processes.append(p)
        # p = multiprocessing.Process(target=onionland, args=(topic, config["keys"][topic]))
        # processes.append(p)

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    logging.info("Crawler finished.")

    return True
