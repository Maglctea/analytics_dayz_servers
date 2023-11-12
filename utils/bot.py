import asyncio
import logging
from datetime import datetime
from typing import Optional, AsyncIterator
import aiohttp
import discord
from discord import Message
from discord.ext.commands import Bot
import traceback
from models import Server
from utils.parser import get_pages, parse_page

logger = logging.getLogger(__name__)


async def get_server_icon(invite_code: str) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"https://discord.com/api/v9/invites/{invite_code}")

        if response.status == 200:
            response = await response.json()
            server = response["guild"]
            avatar_url = f"https://cdn.discordapp.com/icons/{server['id']}/{server['icon']}.png"
            return avatar_url
    return None


async def bulid_embed(invite_code: str = None,
                      server_info: Server = None,
                      registration: str = None,
                      mode: str = None,
                      rating: float = None,
                      description: str = None,
                      bot_icon: str = None,
                      banner_url: str = None
                      ) -> discord.Embed:

    embed = discord.Embed(
        title=server_info.name,
        description=description,
        color=discord.Color.red()
    )

    embed.set_author(
        name='Нажми, чтобы перейти на сервер',
        url=f'https://discord.gg/{invite_code}',
        icon_url=await get_server_icon(invite_code)
    )

    embed.add_field(
        name='Регистрация',
        value=registration,
        inline=True
    )
    embed.add_field(
        name='Режим',
        value=mode,
        inline=True
    )
    embed.add_field(
        name='Карта',
        value=server_info.map,
        inline=True
    )
    embed.add_field(
        name=':busts_in_silhouette: Статус',
        value=f'{"🟢" if server_info.status[1] == "n" else "🔴"} {server_info.status}',
        inline=True
    )
    embed.add_field(
        name=f':link: {server_info.ip}',
        value='\u200b',  # Невидимое значение, чтобы создать отступ
        inline=False
    )

    embed.set_thumbnail(url=f'http://fb79092i.beget.tech/SDCScores/{float(rating)}')

    embed.set_image(url=banner_url)

    now = datetime.now()
    formatted_date = now.strftime("%d.%m.%Y %H:%M:%S")
    embed.set_footer(icon_url=bot_icon,
                     text=f'{server_info.id} | Всего голосов {""} | Дата обновления {formatted_date}')

    return embed


async def get_rating(message: Message) -> float:
    summa = 0
    count = 0
    reactions = message.reactions
    for i in range(5):
        count += reactions[i].count - 1
        summa += (reactions[i].count - 1) * (i + 1)

    if count == 0:
        return 0

    average = round(summa / count, 1)
    return average


async def get_messages(bot: Bot, id_channel: int) -> AsyncIterator[Message]:
    channel = bot.get_channel(id_channel)
    return channel.history()


async def get_message_by_id(bot: Bot, id_channel: int, id_server: int) -> Optional[Message]:
    messages = await get_messages(bot, id_channel)

    async for message in messages:
        if int(message.embeds[0].footer.text.split('|')[0]) == id_server:
            return message

    return None


async def update_embeds(bot: Bot, channel_id: int) -> None:
    messages = await get_messages(bot, channel_id)
    async for message in messages:

        embed = message.embeds[0]
        try:
            id_server = int(embed.footer.text.split('|')[0])
            pages = await get_pages([id_server])
            fields = embed.fields

            embed = await bulid_embed(
                invite_code=embed.author.url.split('/')[-1],
                server_info=parse_page(pages[0]),
                registration=fields[0].value,
                mode=fields[1].value,
                rating=await get_rating(message),
                bot_icon=bot.user.display_avatar.url,
                description=embed.description,
                banner_url=embed.image.url
            )
            await message.edit(embed=embed)
            logger.info(f'{datetime.now()}: {embed.title}: updated')
        except Exception as e:
            logger.exception(f'{datetime.now()}: {embed.title}: {traceback.format_exc()}')

