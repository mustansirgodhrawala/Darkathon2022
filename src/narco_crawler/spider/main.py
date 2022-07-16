# spider/main.py
# This function spiders links in depth and puts them in a kafka pipeline. In a perfect
import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from rich import print as rprint
from w3lib.html import replace_entities

from narco_crawler.config.db import database
from narco_crawler.engines.random_headers import random_headers
from narco_crawler.spider import spider_logger as logging


def spider(db_names, depth=2):
    cursor = database.cursor()
    total = []
    for db in db_names:
        cursor.execute(f"select links from {db}")
        result = cursor.fetchall()
        for i in result:
            total.append(i[0])
    asyncio.run(spider_main(total))
    return True


async def spider_main(links):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for link in links:
            task = asyncio.ensure_future(get_all_links(session, producer, link))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        logging.info("Returning Spider crawler")
        a = 0
        for i in results:
            try:
                a += i
            except Exception:
                pass
        rprint(f"Results: {a}")


async def get_all_links(session, producer, link):
    total = 0
    try:
        async with session.get(
            link,
            headers=random_headers(),
            timeout=180,
        ) as response:
            response = await response.read()
            soup = BeautifulSoup(replace_entities(response), "html5lib")
            for i in soup.find_all("a"):
                if ".onion" in i["href"]:
                    total += 1
        return total
    except asyncio.exceptions.TimeoutError:
        logging.warning("Crawler Timeout handled.")
    except Exception as e:
        logging.critical("Crawler Error")
        logging.exception(e, exc_info=True)
