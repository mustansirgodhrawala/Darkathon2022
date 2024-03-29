import asyncio
import os
import sys
import time
from random import choice
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import unquote

import aiohttp
from aiohttp_socks import ChainProxyConnector
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
            task = asyncio.ensure_future(scrape(session, keyword, producer))
            tasks.append(task)

        links = await asyncio.gather(*tasks)
        mainlog.info(f"Returning tordex crawler for {topic}.")
        engines_logger.info(f"Returning tordex crawler for {topic}.")

        # print(f"Total links received { len(links) }")


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://tordexu73joywapk2txdr54jed4imqledpcvcuf75qsas2gwdgksvnyd.onion"
    )
    tordex_url = tor_address + "/search?query={keyword}&page={page}"
    max_nb_page = 100
    # try:
    async with session.get(
        tordex_url.format(page=1, keyword=keyword), headers=random_headers()
    ) as response:
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
            name = clear(r.get_text())
            link = clear(r["href"])
            if ".onion" in link:
                producer.send(topic, bytes(link, "utf-8"))

        for n in range(2, page_number + 1):
            async with session.get(tordex_url.format(keyword=keyword, page=n)) as resp:
                resp = await resp.read()
                soup = BeautifulSoup(resp, "html5lib")
                for r in soup.select(".container h5 a"):
                    name = clear(r.get_text())
                    link = clear(r["href"])
                    if ".onion" in link:
                        producer.send(topic, bytes(link, "utf-8"))
        # except:
        # print("Failure")

        # return len(link)
    # except Exception as e:
    #     print(f"Timeout caused. {e}")


time_taken = []

start = time.perf_counter()
asyncio.run(main())
print(time.perf_counter() - start)
