import logging
import traceback
from datetime import datetime

from discord import Embed, NotFound
from discord.ext.commands import Bot

from dayz.application.interfaces.server import IServerGateway
from dayz.domain.dto.server import ServerBannerInfoDTO, ServerEmbedDTO
from dayz.infrastructure.parser import parse_page, get_pages
from dayz.presentation.bot.utils.bot import build_embed, get_message_by_message_id, get_rating, get_messages, is_enough_reactions, get_reactions_count, \
    bulid_top_embed

logger = logging.getLogger(__name__)


async def parse_page_service(
        address: str,
        query_port: int | str
) -> ServerBannerInfoDTO:
    pages = await get_pages([f'{address}:{query_port}'])
    server_banner_info = parse_page(pages[0])
    return server_banner_info


async def get_embed(server_info: ServerEmbedDTO) -> Embed:
    server_data = server_info.data
    banner_info = await parse_page_service(
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
        server_gateway: IServerGateway
) -> None:
    servers = await server_gateway.get_servers()

    for server in servers:
        try:
            server = server
            try:
                message = await get_message_by_message_id(bot, channel_id, server.message_id)
            except NotFound as e:
                logger.exception(f'Message for {server.name} not found')
                continue

            pages = await get_pages([f'{server.address}:{server.query_port}'])
            embed = await build_embed(
                server_info=server,
                server_banner_info=parse_page(pages[0]) if pages else None,
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
    server_gateway: IServerGateway
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

    embeds = []
    for message in sorted_message_list[:placing_count]:
        server_data = await server_gateway.get_server(message_id=message.id)
        pages = await get_pages([f'{server_data.address}:{server_data.query_port}'])
        embed = await bulid_top_embed(
            server_info=server_data,
            server_banner_info=parse_page(pages[0]) if pages else None,
            rating=round(get_rating(message), 1),
            bot_icon=bot.user.display_avatar.url,
        )
        embeds.append(embed)

    channel = bot.get_channel(top_channel_id)

    await channel.purge(limit=100, bulk=True)
    try:
        await channel.send(
            embeds=embeds
        )
    except TypeError as e:
        logger.exception(f'Exception {e}. Perhaps too many places have been chosen for the top?')
