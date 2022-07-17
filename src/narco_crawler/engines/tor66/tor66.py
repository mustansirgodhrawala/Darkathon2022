import asyncio
import math
import re
import urllib.parse as urlparse
from urllib.parse import parse_qs

import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer

from narco_crawler.engines import engines_logger as logging
from narco_crawler.engines.random_headers import random_headers


def get_parameter(url, parameter_name):
    parsed = urlparse.urlparse(url)
    return parse_qs(parsed.query)[parameter_name][0]


def clear(toclear):
    str = toclear.replace("\n", " ")
    str = " ".join(str.split())
    return str


async def tor66_main(topic, keywords):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting tor66 crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scrape(session, keyword, producer, topic))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        logging.info(f"Returning tor66 crawler for {topic}, result is {results}")


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion"
    )
    tor66 = tor_address + "/search?q={keyword}&sorttype=rel&page={page}"
    max_nb_page = 100
    result = 0

    try:
        async with session.get(
            tor66.format(page=1, keyword=keyword),
            headers=random_headers(),
            timeout=300,
        ) as response:
            logging.info(f"Tor66 engine for {keyword} called")
            response = await response.read()
            response = response.decode("utf-8")
            soup = BeautifulSoup(response, "html5lib")

            page_number = 1
            approx_re = re.search(r"\.Onion\ssites\sfound\s:\s([0-9]+)", response)
            if approx_re is not None:
                nb_res = int(approx_re.group(1))
                results_per_page = 20
                page_number = math.ceil(float(nb_res / results_per_page))
                logging.info(
                    f"Max page for tor 66 on keyword: {keyword }is {page_number}."
                )
                if page_number > max_nb_page:
                    page_number = max_nb_page

            for i in soup.find("hr").find_all_next("b"):
                if i.find("a"):
                    link = clear(i.find("a")["href"])
                    result += 1
                    producer.send(topic, bytes(link, "utf-8"))

            for n in range(2, page_number + 1):
                try:
                    async with session.get(
                        tor66.format(page=1, keyword=keyword),
                        headers=random_headers(),
                        timeout=180,
                    ) as resp:
                        resp = await resp.read()
                        resp = resp.decode("utf-8")
                        soup = BeautifulSoup(resp, "html5lib")
                        total = 0
                        for i in soup.find("hr").find_all_next("b"):
                            if i.find("a"):
                                link = clear(i.find("a")["href"])
                                total += 1
                                result += 1
                                producer.send(topic, bytes(link, "utf-8"))
                        if total == 0:
                            break

                except (asyncio.TimeoutError,aiohttp.client_exceptions.ServerDisconnectedError):
                    logging.warning(f"Tor66 Timeout on {keyword}, handled.")
                except Exception as e:
                    logging.critical("Tor66 engine error")
                    logging.exception(e, exc_info=True)
    except Exception as e:
        logging.critical("Tor66 Crawler timeout")
        logging.exception(e, exc_info=True)
    return result
