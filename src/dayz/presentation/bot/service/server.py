import asyncio
import logging
import sys
import traceback
from datetime import datetime

import a2s
import discord
from a2s import SourceInfo
from a2s.defaults import DEFAULT_TIMEOUT, DEFAULT_ENCODING
from discord import Embed, NotFound
from discord.ext.commands import Bot

from dayz.application.interfaces.server import IPVPServerGateway
from dayz.domain.dto.server import ServerBannerInfoDTO, ServerEmbedDTO, CreateServerDTO
from dayz.presentation.bot.utils.bot import build_embed, get_message_by_message_id, get_rating, get_messages, is_enough_reactions, get_reactions_count, \
    bulid_top_embed

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


async def get_server_info(address: str, query_port: int) -> ServerBannerInfoDTO | None:
    server = (address, query_port)
    try:
        info: SourceInfo = await a2s.ainfo(server, timeout=DEFAULT_TIMEOUT, encoding=DEFAULT_ENCODING)
    except asyncio.TimeoutError:
        logger.warning(f'Server {address}:{query_port} is not responding for a long time')
        return None
    except ConnectionRefusedError:
        logger.warning(f'Server {address}:{query_port} refused to connect')
        return None

    server_info = ServerBannerInfoDTO(
        status='online',
        players=info.player_count,
        max_players=info.max_players,
        version=info.version,
        map=info.map_name
    )

    return server_info


async def get_embed(server_info: ServerEmbedDTO) -> Embed:
    server_data: CreateServerDTO = server_info.data
    banner_info = await get_server_info(
        address=server_data.address,
        query_port=server_data.query_port
    )

    embed = await build_embed(
        server_info=server_data,
        server_banner_info=banner_info,
        rating=0,
        bot_icon=server_info.avatar_url
    )
    return embed


async def update_embeds_service(
        bot: Bot,
        channel_id: int,
        server_gateway: IPVPServerGateway
) -> None:
    servers = await server_gateway.get_servers()

    for server in servers:
        try:
            message = await get_message_by_message_id(bot, channel_id, server.message_id)
        except NotFound as e:
            logger.exception(f'Message for {server.name} not found')
            continue
        try:
            embed = await build_embed(
                server_info=server,
                server_banner_info=await get_server_info(server.address, server.query_port),
                rating=round(get_rating(message), 1),
                bot_icon=bot.user.display_avatar.url,
            )

            await message.edit(embed=embed)
            logger.info(f'{datetime.now()}: {embed.title}: updated')
        except Exception as e:
            logger.exception(f'{datetime.now()}: {server.name}: {traceback.format_exc()}')


async def update_top(
        bot: Bot,
        embed_channel_id: int,
        top_channel_id: int,
        required_reaction_count: int,
        placing_count: int,
        server_gateway: IPVPServerGateway
) -> None:
    filter_message_list = [
        message
        async for message in await get_messages(bot, embed_channel_id)
        if is_enough_reactions(
            message=message,
            required_reaction_count=required_reaction_count
        )
    ]

    sorted_message_list = sorted(
        filter_message_list,
        key=lambda message: (-get_rating(message), -get_reactions_count(message))
    )

    channel = bot.get_channel(top_channel_id)
    await channel.purge(limit=100, bulk=True)

    embeds = []
    for message in sorted_message_list[:placing_count]:
        server_data = await server_gateway.get_server(message_id=message.id)
        embed = await bulid_top_embed(
            server_info=server_data,
            server_banner_info=await get_server_info(server_data.address, server_data.query_port),
            rating=round(get_rating(message), 1),
            bot_icon=bot.user.display_avatar.url,
        )

        server_link = 'https://discord.com/channels/416292549884641282'
        button_view = (
            discord.ui.View()
            .add_item(discord.ui.Button(emoji='🔗', label='Карточка сервера', url=f'{server_link}/1163130507098333184/{server_data.message_id}'))
            .add_item(discord.ui.Button(emoji='🔗', label='Отзывы сервера', url=f'{server_link}/{server_data.forum_id}'))
        )
        await channel.send(embed=embed, view=button_view)
    try:
        await channel.send(
            embeds=embeds
        )
    except TypeError as e:
        logger.exception(f'Exception {e}. Perhaps too many places have been chosen for the top?')
