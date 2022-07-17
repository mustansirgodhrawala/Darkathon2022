import asyncio
import random
import time
import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from rich import print as rprint

from narco_crawler.config.config import config
from narco_crawler.config.db import database
from narco_crawler.engines.random_headers import random_headers
from narco_crawler.validator import cv
from narco_crawler.validator import model
from narco_crawler.validator import validator_logger as logging
import shutup; shutup.please()


def eliminator(links):
    res = asyncio.run(scanner_main(links))
    finals = []
    for (link, stat) in zip(links, res):
        if stat:
            finals.append(link)
    print(len(finals))
    print(res.count(True))
    return finals


async def scanner_main(links):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting Validator with crawler for {len(links)}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for idx, link in enumerate(links):
            if idx % 100 == 0:
                time.sleep(15)
                logging.info("Taking a rest")
            task = asyncio.ensure_future(scraper(session, producer, link))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        logging.info("Returning Validator crawler.")

        return results


async def scraper(session, producer, link):
    try:
        async with session.get(link, headers=random_headers(), timeout=30) as response:
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")
            [
                s.extract()
                for s in soup(["style", "script", "[document]"])
            ]
            visible_text = soup.getText()
            prediction = model.predict(
                cv.transform([" ".join(visible_text.replace("\n", "").strip().lower().split())])
            )
            # Write Code here to test the soup with the machine learning model
            if prediction == ["drugs"]:
                producer.send("drugs", bytes(link, "utf-8"))
            else:
                producer.send("notdrugs", bytes(link, "utf-8"))
                
            # Write Code here to move the files to the pipelines
            return True
    except asyncio.TimeoutError:
        logging.info("Validator timeout")
    except Exception as e:
        logging.warning(f"Validator warning: {e}")


def validator_base():
    # This function is used to remove and delete all links that are dormant or useless

    # Get all links from database
    cursor = database.cursor()
    for topic in list(config["keys"].keys()):
        cursor.execute(f"select links from {topic}_ingress")
        result = cursor.fetchall()

        links = []
        for link in result:
            links.append(link[0])

        if links:
            links = eliminator(links)
        else:
            rprint(f"\t\t[red]No links for {topic}[/red]")
    return True
