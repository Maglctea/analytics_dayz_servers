import asyncio
from datetime import datetime
from typing import List, Optional

from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
import aiohttp
from models import Server
import logging

logger = logging.getLogger(__name__)

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def get_link(address: int) -> str:
    return f'https://cmsminecraftshop.com/en/query/type/sevendaystodie/ip/{address}/'


async def __get_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    response = await session.get(url, headers=headers)
    content = await response.content.read()
    return content.decode('utf-8')


async def get_pages(addresses: List[str]) -> List[str]:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                     timeout=ClientTimeout(total=5),
                                     trust_env=True
                                     ) as session:
        async with asyncio.TaskGroup() as tg:
            pages = [await tg.create_task(__get_page(session, get_link(address))) for address in addresses]
    return pages


def parse_page(page: str) -> Optional[Server]:
    soup = BeautifulSoup(page, 'html.parser')

    tables = soup.find_all("table")
    informations = {}
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 2:
                key: str = columns[0].text
                value: str = columns[1].text
                informations[key.strip()] = value.strip()

    if informations:
        server_info = Server(
            status='Online' if informations.get('players') else 'Offline',
            address=informations.get('gq_address'),
            port=int(informations.get('port', -1)),
            version=informations.get('version'),
            map=informations.get('map'),
            players=int(informations.get('players', 0)),
            max_players=int(informations.get('maxplayers', 0))
        )
        return server_info
    else:
        return None

# pages = asyncio.run(get_pages(['185.189.255.223:2303']))
# res = parse_page(pages[0])
# pass
