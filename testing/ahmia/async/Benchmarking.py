import asyncio
import os
import sys
import time
from random import choice

import aiohttp
from aiohttp_socks import ChainProxyConnector
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType
from bs4 import BeautifulSoup
from kafka import KafkaProducer


proxies = {
    "http": "socks5h://localhost:9050",
    "https": "socks5h://localhost:9050",
}

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


keywords = [
    "meth buy",
    "meth sell",
    "meth use",
    "meth mumbai",
    "meth india",
    "meth delhi",
    "meth chandigarh",
    "meth kota",
    "meth make india",
    "indian meth" "meth gujrat",
    "metamphetamines in vadodara",
    "meth buy mumbai",
    "meth ship mumbai",
    "meth buy karnataka",
    "ship meth to india",
    "sell meth in india",
    "metamphetamines from india",
    "indian drugs",
    "buy drugs in india",
]


async def main():
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        producer = KafkaProducer(bootstrap_servers="localhost:9092")
        for keyword in keywords:
            task = asyncio.ensure_future(get_video_data(session, keyword, producer))
            tasks.append(task)

        links = await asyncio.gather(*tasks)

        # print(f"Total links received  { len(links) }")
        print(len(links))


async def get_video_data(session, keyword, producer):
    tor_address = (
        "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion"
    )
    ahmia_url = tor_address + f"/search/?q={keyword}"
    try:
        async with session.get(
            ahmia_url, headers=random_headers(), timeout=20
        ) as response:
            response = await response.read()
            soup = BeautifulSoup(response, "html5lib")
            results = []

            for r in soup.select("li.result h4"):
                link = r.find("a")["href"].split("redirect_url=")[1]
                producer.send("ahmia", bytes(link, "utf-8"))
                results.append(link)

            return results
    except Exception as e:
        print(f"Something caused: {e}")


time_taken = []

for i in range(10):
    start = time.perf_counter()
    asyncio.run(main())
    time_taken.append(time.perf_counter() - start)
    print(f"Round {i} time is {time.perf_counter() - start}")

print(f"List of results: {time_taken}")
avg = 0
for times in time_taken:
    avg = times + avg
avg = avg / len(time_taken)
print(f"Average time: {avg}")
