import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer

from narco_crawler.engines import engines_logger as logging
from narco_crawler.engines.random_headers import random_headers


async def ahmia_main(topic, keywords):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting ahmia crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scraper(session, keyword, producer, topic))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        logging.info(
            f"Returning ahmia crawler for {topic}, links are {len(results)} and are {results}."
        )


async def scraper(session, keyword, producer, topic):
    ahmia_address = (
        "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"
    )
    ahmia_url = ahmia_address + f"/search/?q={keyword}"
    try:
        logging.info(f"Ahmia engine for {keyword} called")
        async with session.get(
            ahmia_url, headers=random_headers(), timeout=300
        ) as response:
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")
            results = 0

            for r in soup.select("li.result h4"):
                link = r.find("a")["href"].split("redirect_url=")[1]
                if ".onion" in link:
                    producer.send(topic, bytes(link, "utf-8"))
                    results += 1

    except (asyncio.TimeoutError,aiohttp.client_exceptions.ServerDisconnectedError):
        logging.warning(f"Ahmia engine has timed out on keyword: {keyword}.")
    except Exception as e:
        logging.critical("Unknown exception in ahmia engine.")
        logging.exception(e, exc_info=True)
    return results
