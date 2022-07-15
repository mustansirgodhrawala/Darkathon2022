import asyncio
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


async def haystak_main(topic, keywords):
    connector = connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting haystak crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scrape(session, keyword, producer, topic))
            tasks.append(task)

        await asyncio.gather(*tasks)
        logging.info(f"Returning haystak crawler for {topic}.")


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion/"
    )
    haystak_url = tor_address + "/?q={keyword}&offset={page}"
    max_nb_page = 100
    total = []

    try:
        async with session.get(
            haystak_url.format(page=0, keyword=keyword),
            headers=random_headers(),
            timeout=180,
        ) as response:
            logging.info(f"Haystak engine for {keyword} called")
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")

            # try:
            for r in soup.select(".result b a"):
                link = get_parameter(r["href"], "url")
                producer.send(topic, bytes(link, "utf-8"))
                total.append(link)

            continue_processing = True
            offset_coeff = 20

            if len(total) == 0:
                continue_processing = False

            it = 1
            while continue_processing:
                ret = []
                offset = int(it * offset_coeff)
                async with session.get(
                    haystak_url.format(keyword=keyword, page=offset), timeout=60
                ) as response:
                    response = await response.read()
                    soup = BeautifulSoup(response, "html5lib")
                    for r in soup.select(".result b a"):
                        link = get_parameter(r["href"], "url")
                        producer.send(topic, bytes(link, "utf-8"))
                        ret.append(link)
                    it += 1
                    if it >= max_nb_page or len(ret) == 0:
                        continue_processing = False
    except asyncio.exceptions.TimeoutError:
        logging.warning(f"Haystak Timeout on {keyword}, handled.")
    except Exception as e:
        logging.critical("Haystak engine timeout")
        logging.exception(e, exc_info=True)

    return total
