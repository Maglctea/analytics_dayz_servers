import asyncio
from typing import List, Optional
from bs4 import BeautifulSoup
import aiohttp
from models import Server
import logging

logger = logging.getLogger(__name__)


def get_link(id_page: int) -> str:
    return f'https://wargm.ru/server/{id_page}'


async def __get_page(session: aiohttp.ClientSession, url: str) -> str:
    try:
        response = await session.get(url)
    except Exception as e:
        logger.warning(f'Error link: {url}')
    content = await response.content.read()
    return content.decode('utf-8')


async def get_pages(id_pages: List[int]) -> List[str]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with asyncio.TaskGroup() as tg:
            pages = [await tg.create_task(__get_page(session, get_link(id_page))) for id_page in id_pages]
    return pages


def parse_page(page: str) -> Optional[Server]:
    soup = BeautifulSoup(page, 'html.parser')

    server_name = soup.find('h1').text

    elements = soup.find_all('div', {'class': 'card'})

    if elements:
        info_banner = None
        for element in elements:
            if 'Это мой сервер' in element.text or 'Подтвердить права' in element.text:
                info_banner = element
                break
        if info_banner is None:
            return None

        info_banner = info_banner.find_all('div', {'class': 'f-r ml-5'})
        server_info = Server(
            id=int(info_banner[0].text),
            top=int(info_banner[1].text.split()[0]),
            status=info_banner[2].text,
            ip=info_banner[3].text,
            version=info_banner[4].text,
            map=info_banner[5].text,
            uptime=info_banner[6].text,
            added_at=info_banner[7].text,
            checked_at=info_banner[8].text,
            online_at=info_banner[9].text,
            name=server_name
        )
        return server_info
    else:
        return None

# pages = asyncio.run(get_pages([68350]))
# res = parse_page(pages[0])
# pass
