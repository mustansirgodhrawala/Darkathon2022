import time

from kafka import KafkaConsumer
from rich import print as rprint

from narco_crawler.config import config
from narco_crawler.narco_ingress import ingress_logger


def ingressor(topic):
    total = 0
    ingress_logger.info(f"Ingressor Initiated for topic {topic}")
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
            total = total + len(msg[list(msg.keys())[0]])
        else:
            pass

    rprint(f"\t\t[green]Links for {topic} topic are: {total}.[/green]")


def ingress_main():

    for topic in list(config["keys"].keys()):
        ingressor(topic)

    return True
