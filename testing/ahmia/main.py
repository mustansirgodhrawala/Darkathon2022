import multiprocessing
import time
from random import choice

import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer

times = []
keywords = [
    "meth",
    "buy meth",
    "sell meth",
    "make meth",
    "try meth",
    "ship meth",
    "meth india",
    "meth mumbai",
    "meth delhi",
    "meth punjab",
]
processes = []
# Proxies to specify when using tor for requests.
# SOCKS5H allows us to route dns through the tor network.


# agents used for requests module
desktop_agents = [
    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Android 10; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
    "AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0",
]

tor_address = "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"


def random_headers():
    return {
        "User-Agent": choice(desktop_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }


def ahmia(keyword, port):
    producer = KafkaProducer(bootstrap_servers="localhost:9092")

    # print(f"Ahmia for {keyword} on port {port}")
    proxies = {
        "http": f"socks5h://localhost:{port}",
        "https": f"socks5h://localhost:{port}",
    }

    ahmia_url = tor_address + f"/search/?q={keyword}"

    response = requests.get(ahmia_url, proxies=proxies, headers=random_headers())
    soup = BeautifulSoup(response.text, "html5lib")

    for r in soup.select("li.result h4"):
        link = r.find("a")["href"].split("redirect_url=")[1]
        producer.send("ahmia", bytes(link, "utf-8"))


ports = ["9051", "9052", "9053", "9054", "9055", "9056", "9057", "9058", "9059", "9060"]

for _ in range(10):
    start = time.perf_counter()

    for keyword, port in zip(keywords, ports):
        p = multiprocessing.Process(target=ahmia, args=(keyword, port))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    finish = time.perf_counter()

    time_taken = finish - start
    times.append(time_taken)

print(times)
total_time = 0
for time_taken in times:
    total_time = time_taken + total_time

avg = total_time / len(times)
print(f"Average time = {avg}")
