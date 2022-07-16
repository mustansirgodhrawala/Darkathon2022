import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from kafka import KafkaProducer

from narco_crawler.config.config import config
from narco_crawler.config.db import database
from narco_crawler.engines.random_headers import random_headers
from narco_crawler.sorter import sorter_logger as logging

# from bs4 import BeautifulSoup


def eliminator(links):
    res = asyncio.run(scanner_main(links))
    finals = []
    for (link, stat) in zip(links, res):
        if stat:
            finals.append(link)
    print(len(finals))
    print(res.count(True))
    return finals


async def scanner_main(links):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting sorter with crawler for {len(links)}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for idx, link in enumerate(links):
            # if idx % 100 == 0:
            # time.sleep(10)
            # logging.info("Taking a rest")
            task = asyncio.ensure_future(scraper(session, producer, link))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        logging.info("Returning Eliminator crawler.")

        return results


async def scraper(session, producer, link):
    try:
        async with session.get(link, headers=random_headers(), timeout=300) as response:
            response = await response.read()
            # soup = BeautifulSoup(response, "html5lib")
            return True
    except asyncio.TimeoutError:
        logging.info("Eliminator timeout")
    except Exception as e:
        logging.warning(f"Eliminator warning: {e}")


def sorter_base():
    # This function is used to remove and delete all links that are dormant or useless

    # Get all links from database
    cursor = database.cursor()
    for topic in list(config["keys"].keys()):
        cursor.execute(f"select links from {topic}_ingress")
        result = cursor.fetchall()

        links = []
        for link in result:
            links.append(link[0])

        links = eliminator(links)

    return True
