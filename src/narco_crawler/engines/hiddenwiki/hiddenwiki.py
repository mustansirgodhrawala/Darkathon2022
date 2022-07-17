import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from w3lib.html import replace_entities

from narco_crawler.engines import engines_logger as logging
from narco_crawler.engines.random_headers import random_headers


async def hiddenwiki_main():
    connector = connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info("Starting HiddenWiki crawler")
    async with aiohttp.ClientSession(connector=connector) as session:
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        task = asyncio.ensure_future(scrape(session, producer))

        totals = await asyncio.gather(task)

        logging.info(f"Returning HiddenWiki crawler, links found {totals}")


async def scrape(session, producer):
    tor_address = (
        "http://s4k4ceiapwwgcm3mkb6e4diqecpo7kvdnfr5gg7sph7jjppqkvwwqtyd.onion/"
    )
    total = 0

    try:
        async with session.get(
            tor_address,
            headers=random_headers(),
            timeout=300,
        ) as response:
            response = await response.read()
            logging.info("HiddenWiki engine called")
            soup = BeautifulSoup(replace_entities(response), "lxml")

            for idx, item in enumerate(soup.find_all("h2")):
                try:
                    if str(item["id"]) == "Drugs":
                        no_of_header = idx
                except Exception:
                    continue

            for link in soup.find_all("p")[(no_of_header * 2)].find_all("a"):
                producer.send("markets", bytes(str(link["href"]), "utf-8"))
                total += 1

    except asyncio.exceptions.TimeoutError:
        logging.warning("HiddenWiki Timeout handled.")
    except Exception as e:
        logging.critical("HiddenWiki engine timeout")
        logging.exception(e, exc_info=True)

    return total
