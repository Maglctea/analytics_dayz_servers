import logging
import traceback
from datetime import datetime
from typing import Optional, AsyncIterator

import aiohttp
import discord
from discord import Message
from discord.ext.commands import Bot

from database.orm import get_servers
from schemes import ServerInfo, ServerBannerInfo
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


async def bulid_embed(
        server_info: ServerInfo = None,
        server_banner_info: ServerBannerInfo = None,
        rating: float = None,
        bot_icon: str = None,
) -> discord.Embed:
    embed = discord.Embed(
        title=server_info.name,
        description=server_info.description,
        color=discord.Color.red()
    )

    embed.set_author(
        name='Нажми, чтобы перейти на сервер',
        url=f'https://discord.gg/{server_info.invite_code}',
        icon_url=await get_server_icon(server_info.invite_code)
    )

    embed.add_field(
        name='Регистрация',
        value=server_info.registration_type,
        inline=True
    )
    embed.add_field(
        name='Режим',
        value=server_info.mode,
        inline=True
    )
    if server_banner_info is not None:
        embed.add_field(
            name='Карта',
            value=server_banner_info.map or '?',
            inline=True
        )
        embed.add_field(
            name=':busts_in_silhouette: Статус',
            value=f'{"🟢" if server_banner_info.status[1] == "n" else "🔴"} {server_banner_info.status} {server_banner_info.players}/{server_banner_info.max_players}',
            inline=True
        )
    embed.add_field(
        name=f':link: {server_info.address}:{server_info.port}',
        value='\u200b',  # Невидимое значение, чтобы создать отступ
        inline=False
    )

    embed.set_thumbnail(url=f'http://fb79092i.beget.tech/SDCScores/{float(rating)}')

    embed.set_image(url=server_info.banner_url)

    now = datetime.now()
    formatted_date = now.strftime("%d.%m.%Y %H:%M:%S")
    embed.set_footer(icon_url=bot_icon,
                     text=f'Дата обновления {formatted_date}')

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


async def get_message_by_name(bot: Bot, id_channel: int, name: str) -> Optional[Message]:
    messages = await get_messages(bot, id_channel)

    async for message in messages:
        if message.embeds[0].title == name:
            return message

    return None


async def get_message_by_message_id(bot: Bot, id_channel: int, message_id: int):
    channel = bot.get_channel(id_channel)
    try:
        message = await channel.fetch_message(message_id)
        return message
    except:
        return None


async def update_embeds(bot: Bot, channel_id: int) -> None:
    server_info = get_servers()

    for server in server_info:
        try:
            message = await get_message_by_message_id(bot, channel_id, server.message_id)
            pages = await get_pages([f'{server.address}:{server.query_port}'])
            embed = await bulid_embed(
                server_info=server,
                server_banner_info=parse_page(pages[0]) if pages else None,
                rating=await get_rating(message),
                bot_icon=bot.user.display_avatar.url,
            )

            await message.edit(embed=embed)
            logger.info(f'{datetime.now()}: {embed.title}: updated')
        except Exception as e:
            logger.exception(f'{datetime.now()}: {server.name}: {traceback.format_exc()}')
