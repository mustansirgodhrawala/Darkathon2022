import asyncio
import multiprocessing
import time

from rich import print as rprint

from narco_crawler.config.config import config
from narco_crawler.config.config import maxcores
from narco_crawler.crawler import crawler_logger as logging
from narco_crawler.engines.ahmia.ahmia import ahmia_main
from narco_crawler.engines.haystak.haystak import haystak_main
from narco_crawler.engines.hiddenwiki.hiddenwiki import hiddenwiki_main
from narco_crawler.engines.onionland.onionland import onionland_main
from narco_crawler.engines.onionsearchengine.onionsearchengine import (
    onionsearchengine_main,
)
from narco_crawler.engines.onionsearchserver.onionsearchserver import (
    onionsearchserver_main,
)
from narco_crawler.engines.tor66.tor66 import tor66_main
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


def onionsearchengine(topic, keywords):
    asyncio.run(onionsearchengine_main(topic, config["keys"][topic]))


def haystak(topic, keywords):
    asyncio.run(haystak_main(topic, config["keys"][topic]))


def tor66(topic, keywords):
    asyncio.run(tor66_main(topic, config["keys"][topic]))


def onionsearchserver(topic, keywords):
    asyncio.run(onionsearchserver_main(topic, config["keys"][topic]))


def hiddenwiki():
    asyncio.run(hiddenwiki_main())


def run_crawler():
    logging.info("Crawler run starting.")

    topics = list(config["keys"].keys())

    p = multiprocessing.Pool(maxcores())
    start = time.perf_counter()

    for topic in topics:
        p.apply_async(ahmia, args=(topic, config["keys"][topic]))
        p.apply_async(tordex, args=(topic, config["keys"][topic]))
        p.apply_async(onionland, args=(topic, config["keys"][topic]))
        p.apply_async(onionsearchengine, args=(topic, config["keys"][topic]))
        p.apply_async(haystak, args=(topic, config["keys"][topic]))
        p.apply_async(tor66, args=(topic, config["keys"][topic]))
        p.apply_async(onionsearchserver, args=(topic, config["keys"][topic]))

    p.apply_async(hiddenwiki)

    p.close()
    p.join()

    rprint(f"\t\t[green]Time taken: { time.perf_counter() - start }[/green]")
    logging.info(f"Time taken: { time.perf_counter() - start }")
    logging.info("Crawler finished.")

    return True
