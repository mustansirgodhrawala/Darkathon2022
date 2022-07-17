import asyncio
import json
import os
from random import choice

import aiohttp
import mysql.connector
from aiohttp_socks import ProxyConnector
from aiohttp_socks import ProxyType

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


def random_headers():
    return {
        "User-Agent": choice(desktop_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }


def ImportConfig(config_file):
    try:
        with open(config_file) as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        exit()


# Config Init
try:
    file = os.environ.get("config_file")
    if file is None:
        exit()
    else:
        config = ImportConfig(str(file))
except Exception:
    exit()

mydb = mysql.connector.connect(
    host=config["database"]["host"],
    user=config["database"]["user"],
    password=config["database"]["pass"],
    database=config["database"]["db"],
)
cursor = mydb.cursor()
print("Cursor Created")

print("Getting Links")
for topic in list(config["keys"].keys()):
    cursor.execute(f"SELECT links FROM {topic}_ingress")
    myresult = cursor.fetchall()

print(myresult)
exit()
print("Fetching dataset.")


async def main(links):
    connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS5, host="localhost", port=9050, rdns=True
    )
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for link in links:
            task = asyncio.ensure_future(get_video_data(session, link))
            tasks.append(task)

        links = await asyncio.gather(*tasks)


async def get_video_data(session, link):
    try:
        async with session.get(link, headers=random_headers(), timeout=20) as response:
            response = await response.read()
            print(response)
            exit()
    except Exception as e:
        print(e)


asyncio.run(main(myresult))
