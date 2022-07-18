import asyncio
import random
import time
import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from kafka import KafkaConsumer
from rich import print as rprint

from narco_crawler.config.config import config
from narco_crawler.config.db import database
from narco_crawler.engines.random_headers import random_headers
from narco_crawler.validator import cv
from narco_crawler.validator import model
from narco_crawler.validator import validator_logger as logging
import shutup; shutup.please()


def eliminator(topic, links):
    res = asyncio.run(scanner_main(links))
    finals = []
    for (link, stat) in zip(links, res):
        if stat:
            finals.append(link)
    rprint(f"[green]{ res.count(True) } links are valid in topic, {topic}[/green]")
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
            links = eliminator(links,topic)
        else:
            rprint(f"\t\t[red]No links for {topic}[/red]")
    return True

def validator_primary():
    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        max_poll_records=100000000,
    )

    links = []

    consumer.subscribe(["spidered_drugs"])
    for _ in range(20):
        msg = consumer.poll(1)
        if not msg == {}:
            for messages in msg[list(msg.keys())[0]]:
                link = messages.value.decode("UTF-8")
                links.append(link)
        else:
            pass
    consumer2 = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        max_poll_records=100000000,
    )
    consumer2.subscribe(["spidered_notdrugs"])
    for _ in range(20):
        msg = consumer2.poll(1)
        if not msg == {}:
            for messages in msg[list(msg.keys())[0]]:
                link = messages.value.decode("UTF-8")
                links.append(link)
        else:
            pass
    rprint("\t\t[green]Validator found a total of len(links), after spidering, now analyzing these links.[/green]")
    asyncio.run(scanner_primary(links))

async def scanner_primary(links):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    logging.info(f"Starting Validator Second Run with crawler for {len(links)}.")
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for idx, link in enumerate(links):
            if idx % 100 == 0:
                time.sleep(15)
                logging.info("Taking a rest")
            task = asyncio.ensure_future(scraper_primary(session, producer, link))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        logging.info("Returning Validator Second Run.")

        return results


async def scraper_primary(session, producer, link):
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
                producer.send("final_drugs", bytes(link, "utf-8"))
                
            # Write Code here to move the files to the pipelines
            return True
    except asyncio.TimeoutError:
        logging.info("Validator timeout")
    except Exception as e:
        logging.warning(f"Validator warning: {e}")