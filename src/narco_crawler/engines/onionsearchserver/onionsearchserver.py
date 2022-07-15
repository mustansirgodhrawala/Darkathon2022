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


async def onionsearchserver_main(topic, keywords):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting OnionSearchServer crawler for {topic}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(scrape(session, keyword, producer, topic))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        logging.info(
            f"Returning OnionSearchServer crawler for {topic}, result is {results}"
        )


async def scrape(session, keyword, producer, topic):
    tor_address = (
        "http://3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion/oss/"
    )

    onionsearchserver = tor_address + "?query={keyword}&thumbs=off"

    result = 0

    try:
        async with session.get(
            onionsearchserver.format(keyword=keyword),
            headers=random_headers(),
            timeout=180,
        ) as response:
            logging.info(f"OnionSearchServer engine for {keyword} called")
            response = await response.read()
            response = response.decode("utf-8")
            soup = BeautifulSoup(response, "html5lib")

            for r in soup.select(".osscmnrdr.ossfieldrdr1 a"):
                link = clear(r["href"])
                result += 1
                producer.send(topic, bytes(link, "utf-8"))

    except asyncio.exceptions.TimeoutError:
        logging.warning(f"OnionSearchServer crawler timeout on {keyword}, handled.")
    except Exception as e:
        logging.critical("OnionSearchServer crawler error")
        logging.exception(e, exc_info=True)
    return result
