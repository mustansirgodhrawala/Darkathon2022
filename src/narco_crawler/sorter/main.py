from rich import print as rprint
from narco_crawler.sorter import sorter_logger as logging
from narco_crawler.config.config import config
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaConsumer
from kafka import KafkaProducer
from rich import print as rprint
from narco_crawler.engines.random_headers import random_headers
from collections import OrderedDict
import time

# Drugs pipeline -> final_drugs
def sorter():

	# Words that qualify as Indian drug markets
	words = read_words()

	# Read Messages First 
	links = read_messages()

	# Run sorter
	asyncio.run(scanner(links,words))

	# Sorter ingress
	from narco_crawler.ingress.main import final_ingress
	final_ingress()


	return True


def read_words():
	try:
		words = config["trigger_words"]
		if words:
			return words
		else:
			return None
	except KeyError:
		logging.warning("No keywords loaded into config, for trigger. All websites will qualify")
		return None


async def scanner(links, words):
	connector = ProxyConnector(
		proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
	)
	logging.info(f"Starting Sorter scraping, with links {len(links)}.")
	async with aiohttp.ClientSession(connector=connector) as session:
		tasks = []
		producer = KafkaProducer(bootstrap_servers="localhost:9092")
		for idx, link in enumerate(links):
			if idx % 100 == 0:
				time.sleep(15)
				logging.info("Taking a rest")
			task = asyncio.ensure_future(scraper_primary(session, producer, link, words))
			tasks.append(task)

		results = await asyncio.gather(*tasks)

		logging.info("Returning Sorter Run.")

		return results


async def scraper_primary(session, producer, link, words):
	try:
		async with session.get(link, headers=random_headers(), timeout=30) as response:
			response = await response.read()
			soup = BeautifulSoup(response, "html5lib")
			[
				s.extract()
				for s in soup(["style", "script", "[document]"])
			]
			hits = 0
			visible_text = soup.getText()
			test = [visible_text.replace("\n", "").strip().lower().split()]

			for word in words:
				if word in test:
					hits += 1
			   
			if hits >= 2:
				producer.send("sorter_positive",bytes(link,'utf-8'))
			else:
				producer.send("sorter_negative",bytes(link, 'utf-8'))
			return True
	except asyncio.TimeoutError:
		logging.info("Sorter timeout")
	except Exception as e:
		logging.warning(f"Sorter warning: {e}")


def remove_duplicates(links):
	logging.info(f"Removing duplicates for sorter, initial count { len(links) }")
	links = list(OrderedDict.fromkeys(links))
	logging.info(f"Removed duplicates for sorter, final count { len(links) }")
	return links

def read_messages():
	links = []
	logging.info("Reading links into sorter")
	rprint("\t\t[green]Sorter reading links.[/green]")
	consumer = KafkaConsumer(
		bootstrap_servers=["localhost:9092"],
		auto_offset_reset="earliest",
		max_poll_records=100000000,
	)
	consumer.subscribe(["meth"])

	for _ in range(20):
		msg = consumer.poll(1)
		if not msg == {}:
			for messages in msg[list(msg.keys())[0]]:
				link = messages.value.decode("UTF-8")
				links.append(link)
		else:
			pass

	return remove_duplicates(links)
