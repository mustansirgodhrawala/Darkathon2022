import time

from kafka import KafkaConsumer
from rich import print as rprint

from narco_crawler.config.config import config
from narco_crawler.config.db import database
from narco_crawler.ingress import ingress_logger as logging


def processor(topic, links):
    logging.info(f"Processor called {topic}")
    cursor = database.cursor()
    for link in links:
        cursor.execute(f'INSERT INTO {topic}_ingress(links) VALUES ("{link}")')
    database.commit()
    cursor.close()
    logging.info(f"Processor finished for {topic}, added { len(links) }.")


def ingressor(topic):
    links = []
    logging.info(f"Ingressor Initiated for topic {topic}")
    rprint(f"\t\t[green]Ingressing {topic}.[/green]")
    time.sleep(5)
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

    processor(topic, links)
    logging.info(f"Ingressor finished for topic {topic}")


def ingress_main():

    for topic in list(config["keys"].keys()):
        ingressor(topic)

    return True
