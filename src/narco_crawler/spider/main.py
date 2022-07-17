# spider/main.py
# This function spiders links in depth and puts them in a kafka pipeline. In a perfect
import asyncio
import itertools
import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from rich import print as rprint
from w3lib.html import replace_entities
from kafka import KafkaConsumer
from narco_crawler.config.db import database
from narco_crawler.engines.random_headers import random_headers
from narco_crawler.spider import spider_logger as logging
import multiprocessing
from narco_crawler.ingress.main import ingress_spider

def drugs_spider():
    links = []
    # Pulling links from drugs and notdrugs pipelines in kafka.
    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        max_poll_records=100000000,
    )
    consumer.subscribe(["drugs"])
    for _ in range(20):
        msg = consumer.poll(1)
        if not msg == {}:
            for messages in msg[list(msg.keys())[0]]:
                link = messages.value.decode("UTF-8")
                links.append(link)
        else:
            pass

    # Spidering Links
    print(f"\t\tFound {len(links)} amount of drugs link.")
    links_spidered = asyncio.run(spider_main(links, 1,"spidered_drugs"))


def notdrugs_spider():
    links = []
    # Pulling links from drugs and notdrugs pipelines in kafka.
    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        max_poll_records=100000000,
    )
    consumer.subscribe(["notdrugs"])
    for _ in range(20):
        msg = consumer.poll(1)
        if not msg == {}:
            for messages in msg[list(msg.keys())[0]]:
                link = messages.value.decode("UTF-8")
                links.append(link)
        else:
            pass

    # Spidering Links
    print(f"\t\tFound {len(links)} amount of drugs link.")
    links_spidered = asyncio.run(spider_main(links, 1,"spidered_drugs"))


def spider():
    p1 = multiprocessing.Process(target=drugs_spider)
    p2 = multiprocessing.Process(target=notdrugs_spider)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    ingress_spider()
    return True


async def spider_main(results,depth,pipeline):
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    for i in results:
        producer.send(pipeline,bytes(i,"utf-8"))
    final_deliver = []
    for i in range(1,depth+1):
        logging.info(f"Spider crawler for depth {i}, category is {pipeline}")
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            logging.info(f"Depth of {i} and links are: {len(results)}")
            for link in results:
                task = asyncio.ensure_future(get_all_links(session, producer, link,pipeline))
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            final_deliver = list(itertools.chain.from_iterable(results))
            results = final_deliver
            logging.info(f"Returning Spider crawler for depth {i}, category is {pipeline}")

    logging.info(f"Returning Spider crawler and the links are in total {len(results)}")
    rprint(f"[green]\t\tReturning Spider crawler and the links are in total {len(results)}[/green]")
    return True

async def get_all_links(session, producer, link, pipeline):
    total = []
    try:
        async with session.get(
            link,
            headers=random_headers(),
            timeout=300,
        ) as response:
            # producer.send(pipeline, bytes(link,"utf-8"))
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")
            for i in soup.find_all("a"):
                try:
                    if ".onion" in i["href"]:
                        total.append(i["href"])
                        producer.send(pipeline, bytes(i["href"],"utf-8"))
                except KeyError:
                    pass
    except (asyncio.exceptions.TimeoutError,python_socks._errors.ProxyError,aiohttp.client_exceptions.ServerDisconnectedError):
        logging.warning("Crawler Timeout handled.")
    except Exception as e:
        logging.critical("Crawler Error")
        logging.exception(e,exc_info=True)
    finally:
        return total