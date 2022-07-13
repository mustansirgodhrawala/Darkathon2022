import asyncio
import math
import re
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer

from narco_crawler import logging as mainlog
from narco_crawler.engines import engines_logger
from narco_crawler.engines.random_headers import random_headers


def get_parameter(url, parameter_name):
    parsed = urlparse.urlparse(url)
    return parse_qs(parsed.query)[parameter_name][0]


def clear(toclear):
    str = toclear.replace("\n", " ")
    str = " ".join(str.split())
    return str


async def onionland_main(topic, keywords):
    connector = connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    mainlog.info(f"Starting onionland crawler for {topic}.")
    engines_logger.info(f"Starting onionland crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scrape(session, keyword, producer, topic))
            tasks.append(task)

        await asyncio.gather(*tasks)
        mainlog.info(f"Returning onionland crawler for {topic}.")
        engines_logger.info(f"Returning onionland crawler for {topic}.")


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion"
    )
    onionland_url = tor_address + "/search?q={keyword}&page={page}"
    max_nb_page = 100
    total = []

    try:
        async with session.get(
            onionland_url.format(page=1, keyword=keyword),
            headers=random_headers(),
            timeout=180,
        ) as response:
            engines_logger.info(f"Onionland engine for {keyword} called")
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")

            page_number = 1
            for i in soup.find_all("div", attrs={"class": "search-status"}):
                approx_re = re.match(
                    r"About ([,0-9]+) result(.*)",
                    clear(i.find("div", attrs={"class": "col-sm-12"}).get_text()),
                )
                if approx_re is not None:
                    nb_res = int((approx_re.group(1)).replace(",", ""))
                    results_per_page = 19
                    page_number = math.ceil(nb_res / results_per_page)
                    if page_number > max_nb_page:
                        page_number = max_nb_page

            for r in soup.select(".result-block .title a"):
                if not r["href"].startswith("/ads/"):
                    link = unquote(unquote(get_parameter(r["href"], "l")))
                    producer.send(topic, bytes(link, "utf-8"))

            for n in range(2, page_number + 1):
                try:
                    async with session.get(
                        onionland_url.format(keyword=keyword, page=n), timeout=120
                    ) as resp:
                        resp = await resp.read()
                        soup = BeautifulSoup(resp, "html5lib")
                        total = 0
                        for r in soup.select(".result-block .title a"):
                            if not r["href"].startswith("/ads/"):
                                link = unquote(unquote(get_parameter(r["href"], "l")))
                                if link:
                                    total += 1
                                    producer.send(topic, bytes(link, "utf-8"))
                        if total == 0:
                            break

                except asyncio.exceptions.TimeoutError:
                    engines_logger.warning(f"Onionland Timeout on {keyword}, handled.")
                except Exception as e:
                    engines_logger.critical("Onionland engine timeout")
                    engines_logger.exception(e, exc_info=True)
    except Exception as e:
        engines_logger.critical("Onionland engine timeout")
        engines_logger.exception(e, exc_info=True)

    engines_logger.info(f"Onionland engine for {keyword} returned")
    return total
