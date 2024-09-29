import logging
from datetime import datetime
from typing import Optional, AsyncIterator

import aiohttp
import discord
from discord import Message, User
from discord.ext.commands import Bot

from dayz.domain.dto.server import ServerBannerInfoDTO, ServerDTO, BaseServerDTO

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


def get_color_by_rating(rating: float) -> int:
    if rating == 5:
        return 0x33ff24
    elif rating >= 4.5:
        return 0x249002
    elif rating >= 4.0:
        return 0xded100
    elif rating >= 3:
        return 0xde8800
    elif rating >= 2:
        return 0xff0101
    else:
        return 0x4c0202


async def build_embed(
        server_info: BaseServerDTO = None,
        server_banner_info: ServerBannerInfoDTO = None,
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
    embed.set_footer(
        icon_url=bot_icon,
        text=f'Дата обновления {formatted_date}'
    )
    return embed


async def bulid_top_embed(
        server_info: ServerDTO = None,
        server_banner_info: ServerBannerInfoDTO = None,
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
        name=f':link: {server_info.address}:{server_info.port}',
        value='\u200b',  # Невидимое значение, чтобы создать отступ
        inline=False
    )

    embed.set_thumbnail(url=f'http://fb79092i.beget.tech/SDCScores/{float(rating)}')

    embed.set_image(url=server_info.banner_url)

    now = datetime.now()
    formatted_date = now.strftime("%d.%m.%Y %H:%M:%S")
    embed.set_footer(
        icon_url=bot_icon,
        text=f'Дата обновления {formatted_date}'
    )
    return embed


def get_rating(message: Message) -> float:
    summa = 0
    count = 0
    reactions = message.reactions
    for i in range(5):
        count += reactions[i].count - 1
        summa += (reactions[i].count - 1) * (i + 1)

    if count == 0:
        return 0

    average = summa / count
    return average


async def get_messages(
        bot: Bot,
        id_channel: int
) -> AsyncIterator[Message]:
    channel = bot.get_channel(id_channel)
    return channel.history()


async def get_message_by_name(
        bot: Bot,
        id_channel: int,
        name: str
) -> Optional[Message]:
    messages = await get_messages(
        bot=bot,
        id_channel=id_channel
    )
    async for message in messages:
        if message.embeds[0].title == name:
            return message
    return None


async def get_message_by_message_id(
        bot: Bot,
        id_channel: int,
        message_id: int
) -> Message:
    channel = bot.get_channel(id_channel)
    message = await channel.fetch_message(message_id)
    return message


def get_forum_channel_by_name(
        bot: Bot,
        id_forum: int,
        name: str
) -> discord.Thread | None:
    forum: discord.ForumChannel = bot.get_channel(id_forum)
    for thread in forum.threads:
        if thread.name == name:
            return thread


async def get_user_by_id(
        bot: Bot,
        user_id: int
) -> User:
    user = await bot.fetch_user(user_id)
    return user


def get_reactions_count(message: Message) -> int:
    total_count = 0
    for reaction in message.reactions:
        total_count += reaction.count
    total_count -= 5  # bot reactions count
    return total_count


def is_enough_reactions(
        message: Message,
        required_reaction_count: int
) -> bool:
    if get_reactions_count(message) >= required_reaction_count:
        return True
    return False
