import multiprocessing
from collections import OrderedDict

from kafka import KafkaConsumer
from rich import print as rprint

from narco_crawler.config.config import config
from narco_crawler.config.db import database
from narco_crawler.ingress import ingress_logger as logging


def processor(topic, links):
    logging.info(f"Processor called {topic}")
    cursor = database.cursor()
    # print(links)
    for link in links:
        try:
            sql = f"INSERT INTO {topic}_ingress(links) VALUES (%s)"
            cursor.execute(sql, (link,))
        except Exception as e:
            rprint(
                f"\t\t[red]Problem with ingress on {link} and type is {type(link)}[/red]"
            )
            logging.critical(e)
        # cursor.execute(f'INSERT INTO {topic}_ingress(links) VALUES ("{link}")')
    database.commit()
    if len(links) > 0:
        rprint(f"[green]\t\tIngress finished for {topic}, with { len(links) }[/green]")
    else:
        logging.warning(f"Processor was given zero links for {topic}")
    logging.info(f"Processor finished for {topic}, added { len(links) }.")


def remove_duplicates(topic, links):
    logging.info(f"Removing duplicates for topic {topic}, initial count { len(links) }")
    links = list(OrderedDict.fromkeys(links))
    logging.info(f"Removed duplicates for topic {topic}, final count { len(links) }")
    return links


def topic_ingressor(topic):
    links = []
    logging.info(f"Topics Ingressor for topic {topic}")
    rprint(f"\t\t[green]Ingressing {topic}.[/green]")
    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        max_poll_records=100000000,
    )
    consumer.subscribe([topic])

    for _ in range(20):
        msg = consumer.poll(1)
        if not msg == {}:
            for messages in msg[list(msg.keys())[0]]:
                link = messages.value.decode("UTF-8")
                links.append(link)
        else:
            pass

    links = remove_duplicates(topic, links)
    processor(topic, links)


def market_ingress():
    links = []
    logging.info("Markets Ingress")
    rprint("\t\t[green]Ingressing markets.[/green]")
    consumer = KafkaConsumer(
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        max_poll_records=100000000,
    )
    consumer.subscribe(["markets"])

    for _ in range(20):
        msg = consumer.poll(1)
        if not msg == {}:
            for messages in msg[list(msg.keys())[0]]:
                link = messages.value.decode("UTF-8")
                links.append(link)
        else:
            pass

    links = remove_duplicates("markets", links)
    processor("markets", links)


def ingress_main():
    processes = []

    # Topic Ingressor
    for topic in list(config["keys"].keys()):
        p = multiprocessing.Process(target=topic_ingressor, args=(topic,))
        p.start()
        processes.append(p)

    # Markets Ingressor
    p = multiprocessing.Process(target=market_ingress)
    p.start()
    processes.append(p)

    for process in processes:
        process.join()
    return True
