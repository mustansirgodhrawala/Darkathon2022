import asyncio

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer

from narco_crawler import logging as mainlog
from narco_crawler.engines import engines_logger
from narco_crawler.engines.random_headers import random_headers


def clear(toclear):
    str = toclear.replace("\n", " ")
    str = " ".join(str.split())
    return str


async def tordex_main(topic, keywords):
    connector = connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    mainlog.info(f"Starting tordex crawler for {topic}.")
    engines_logger.info(f"Starting tordex crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scrape(session, keyword, producer, topic))
            tasks.append(task)

        await asyncio.gather(*tasks)
        mainlog.info(f"Returning tordex crawler for {topic}.")
        engines_logger.info(f"Returning tordex crawler for {topic}.")


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://tordexu73joywapk2txdr54jed4imqledpcvcuf75qsas2gwdgksvnyd.onion"
    )
    tordex_url = tor_address + "/search?query={keyword}&page={page}"
    max_nb_page = 100
    total = []

    # try:
    async with session.get(
        tordex_url.format(page=1, keyword=keyword), headers=random_headers()
    ) as response:
        engines_logger.info(f"Tordex engine for {keyword} called")
        response = await response.read()
        soup = BeautifulSoup(response, "html5lib")

        page_number = 1
        pages = soup.find_all("li", attrs={"class": "page-item"})
        if pages is not None:
            for i in pages:
                if i.get_text() != "...":
                    page_number = int(i.get_text())
            if page_number > max_nb_page:
                page_number = max_nb_page

        # try:
        for r in soup.select(".container h5 a"):
            link = clear(r["href"])
            if ".onion" in link:
                producer.send(topic, bytes(link, "utf-8"))
                total.append(link)

        for n in range(2, page_number + 1):
            try:
                async with session.get(
                    tordex_url.format(keyword=keyword, page=n), timeout=60
                ) as resp:
                    resp = await resp.read()
                    soup = BeautifulSoup(resp, "html5lib")
                    for r in soup.select(".container h5 a"):
                        link = clear(r["href"])
                        if ".onion" in link:
                            total.append(link)
                            producer.send(topic, bytes(link, "utf-8"))
            except asyncio.exceptions.TimeoutError:
                engines_logger.warning(f"Tordex Timeout on {keyword}, handled.")
            except Exception as e:
                engines_logger.critical("Tordex engine timeout")
                engines_logger.exception(e, exc_info=True)

        engines_logger.info(f"Tordex engine for {keyword} returned")
        return total
