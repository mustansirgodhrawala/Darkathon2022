import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer

from narco_crawler import logging as mainlog
from narco_crawler.engines import engines_logger
from narco_crawler.engines.random_headers import random_headers


async def ahmia_main(topic, keywords):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    mainlog.info(f"Starting ahmia crawler for {topic}.")
    engines_logger.info(f"Starting ahmia crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scraper(session, keyword, producer, topic))
            tasks.append(task)

        await asyncio.gather(*tasks)
        mainlog.info(f"Returning ahmia crawler for {topic}.")
        engines_logger.info(f"Returning ahmia crawler for {topic}.")


async def scraper(session, keyword, producer, topic):
    ahmia_address = (
        "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"
    )
    ahmia_url = ahmia_address + f"/search/?q={keyword}"
    try:
        engines_logger.info(f"Ahmia engine for {keyword} called")
        async with session.get(
            ahmia_url, headers=random_headers(), timeout=20
        ) as response:
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")
            results = 0

            for r in soup.select("li.result h4"):
                link = r.find("a")["href"].split("redirect_url=")[1]
                producer.send(topic, bytes(str(link), "utf-8"))
                results += 1

            engines_logger.info(
                f"Ahmia engine for {keyword} returned, with {results} links."
            )
            return results
    except asyncio.TimeoutError:
        engines_logger.warning(f"Ahmia engine has timed out on keyword: {keyword}.")
    except Exception as e:
        mainlog.critical(
            f"Ahmia engine has errored. Check engines log for more info. Exception is: {e}"
        )
        engines_logger.critical("Unknown exception in ahmia engine.")
        engines_logger.exception(e, exc_info=True)
