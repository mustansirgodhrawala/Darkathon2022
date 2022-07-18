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
        topic_ingressor(topic)

    # Markets Ingressor
    market_ingress()
    return True

def ingress_spider():
    rprint("\t\t[green]Ingressing Spider Links[/green]")
    p1 = multiprocessing.Process(target=topic_ingressor, args=("spidered_drugs",))
    p1.start()
    p2 = multiprocessing.Process(target=topic_ingressor, args=("spidered_notdrugs",))
    p2.start()
    rprint("\t\t[green]Waiting for ingress to complete.[/green]")
    p1.join()
    p2.join()
    rprint("\t\t[green]Ingress is complete.[/green]")

def final_ingress():
    rprint("\t\t[green]Ingressing sorter links[/green]")
    p1 = multiprocessing.Process(target=sorter_ingressor, args=("sorter_positive","drug_india_sites"))
    p1.start()
    p2 = multiprocessing.Process(target=sorter_ingressor, args=("sorter_negative","drug_sites"))
    p2.start()
    rprint("\t\t[green]Waiting for ingress to complete.[/green]")
    p1.join()
    p2.join()
    rprint("\t\t[green]Ingress is complete[/green]")


def sorter_ingressor(topic, dbname):
    links = []
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
    logging.info(f"Processing called {topic}")
    cursor = database.cursor()
    # print(links)
    for link in links:
        try:
            sql = f"INSERT INTO {dbname}(links) VALUES (%s)"
            cursor.execute(sql, (link,))
        except Exception as e:
            rprint(
                f"\t\t[red]Problem with sorter ingress on {link} and type is {type(link)}[/red]"
            )
            logging.critical(e)
        # cursor.execute(f'INSERT INTO {topic}_ingress(links) VALUES ("{link}")')
    database.commit()
    if len(links) > 0:
        rprint(f"[green]\t\tIngress finished for {topic}, with { len(links) }[/green]")
    else:
        logging.warning(f"Processor was given zero links for {topic}")
    logging.info(f"Processor finished for {topic}, added { len(links) }.")