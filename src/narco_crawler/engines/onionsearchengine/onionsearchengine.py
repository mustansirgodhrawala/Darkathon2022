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


async def onionsearchengine_main(topic, keywords):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting onionsearchengine crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scrape(session, keyword, producer, topic))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        logging.info(
            f"Returning onionsearchengine crawler for {topic}, result is {results}"
        )


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://kn3hl4xwon63tc6hpjrwza2npb7d4w5yhbzq7jjewpfzyhsd65tm6dad.onion"
    )
    onionsearchengine_url = (
        tor_address + "/search.php?search={keyword}&submit=Search&page={page}"
    )
    max_nb_page = 100
    result = 0

    try:
        async with session.get(
            onionsearchengine_url.format(page=1, keyword=keyword),
            headers=random_headers(),
            timeout=300,
        ) as response:
            logging.info(f"OnionSearchEngine engine for {keyword} called")
            response = await response.read()
            response = response.decode("utf-8")
            soup = BeautifulSoup(response, "html5lib")

            page_number = 1
            approx_re = re.search(
                r"\s([0-9]+)\sresult[s]?\sfound\s!.*",
                clear(soup.find("body").get_text()),
            )
            if approx_re is not None:
                nb_res = int(approx_re.group(1))
                results_per_page = 9
                page_number = math.ceil(float(nb_res / results_per_page))
                if page_number > max_nb_page:
                    page_number = max_nb_page

            for r in soup.select("table a b"):
                link = get_parameter(r.parent["href"], "u")
                if link:
                    result += 1
                    producer.send(topic, bytes(link, "utf-8"))

            for n in range(2, page_number + 1):
                try:
                    async with session.get(
                        onionsearchengine_url.format(keyword=keyword, page=n),
                        timeout=30,
                    ) as resp:
                        resp = await resp.read()
                        soup = BeautifulSoup(resp, "html5lib")
                        total = 0
                        for r in soup.select("table a b"):
                            link = get_parameter(r.parent["href"], "u")
                            if link:
                                total += 1
                                result += 1
                                producer.send(topic, bytes(link, "utf-8"))
                        if total == 0:
                            break

                except (asyncio.TimeoutError,aiohttp.client_exceptions.ServerDisconnectedError):
                    logging.warning(f"OnionSearchEngine Timeout on {keyword}, handled.")
                except Exception as e:
                    logging.critical("OnionSearchEngine engine error")
                    logging.exception(e, exc_info=True)
    except Exception as e:
        logging.critical("OnionSearchEngine Crawler timeout")
        logging.exception(e, exc_info=True)
    return result
