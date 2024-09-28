import asyncio
import logging
from typing import List, Optional

import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup

from dayz.domain.dto.server import ServerBannerInfoDTO

logger = logging.getLogger(__name__)

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def get_link(address: str) -> str:
    return f'https://cmsminecraftshop.com/en/query/type/sevendaystodie/ip/{address}/ajax/'


async def _get_page(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    await session.get(url, headers=headers)
    response = await session.get(url, headers=headers)
    content = await response.content.read()
    return content.decode('utf-8')


async def get_pages(addresses: List[str]) -> List[str]:
    async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False, limit=3),
            timeout=ClientTimeout(total=30),
            trust_env=True
    ) as session:
        async with asyncio.TaskGroup() as tg:
            pages = [await tg.create_task(_get_page(session, get_link(address))) for address in addresses]
    return pages


def parse_page(page: str) -> Optional[ServerBannerInfoDTO]:
    soup = BeautifulSoup(page, 'html.parser')

    tables = soup.find_all("table")
    informations = {}
    for table in tables:
        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) == 2:
                key: str = columns[0].text
                value: str = columns[1].text
                informations[key.strip()] = value.strip()

    if not informations:
        return None

    try:
        server_info = ServerBannerInfoDTO(
            status='Online' if informations.get('players') else 'Offline',
            players=int(informations.get('players', 0)),
            max_players=int(informations.get('maxplayers', 0)),
            version=informations.get('version'),
            map=informations.get('map')
        )
        return server_info

    except Exception as e:
        logger.error(f'Error: {e}')
