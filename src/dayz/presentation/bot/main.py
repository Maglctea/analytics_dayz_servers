import asyncio
import logging
import os
import sys
from datetime import datetime
from distutils.command.config import config

import discord
import pytz
from discord import Interaction, User, ButtonStyle, Member, RawReactionActionEvent
from discord.ext import commands, tasks
from dishka import make_async_container, AsyncContainer, FromDishka
from dishka.integrations.faststream import inject, setup_dishka
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from dayz import config
from dayz.application.interfaces.server import IPVPServerGateway, IPVEServerGateway
from dayz.application.interfaces.uow import IUoW
from dayz.config import BotConfig, StorageConfig, BrokerConfig, AuthConfig, APIConfig, AdminConfig, DBConfig
from dayz.domain.dto.server import ServerEmbedDTO, ServerDTO, CreateServerDTO
from dayz.infrastructure.di.db import DbProvider
from dayz.infrastructure.di.gateway import GatewaysProvider
from dayz.presentation.bot.service.reactions import clear_user_reactions
from dayz.presentation.bot.service.server import get_embed, update_embeds_service, update_top
from dayz.presentation.bot.utils.bot import get_message_by_message_id, get_forum_channel_by_name, get_user_by_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all()
)
container: AsyncContainer = ...
broker = RabbitBroker(url=config.broker_config.url)
app = FastStream(broker)


async def add_server_process(server_gateway: IPVPServerGateway | IPVEServerGateway, uow: IUoW, server: CreateServerDTO,
                             channel_embeds_id: int,
                             forum_feedback_id: int):
    server_data = ServerEmbedDTO(
        avatar_url=bot.user.avatar.url,
        data=server
    )

    embed = await get_embed(server_data)
    channel = bot.get_channel(channel_embeds_id)

    server_card = await channel.send(embed=embed)

    for i in range(1, 6):
        emoji = f'{i}\u20e3'  # Получаем соответствующий эмодзи
        await server_card.add_reaction(emoji)

    forum: discord.ForumChannel = bot.get_channel(forum_feedback_id)

    embed = discord.Embed(
        title=server.name,
        description=f'Тут вы можете оставить отзыв или посмотреть информацию о сервере {server.name}'
    )
    view_feedback_card = discord.ui.View().add_item(
        discord.ui.Button(emoji='🔗', label='Карточка сервера', url=server_card.jump_url))

    server_feedback_channel = await forum.create_thread(
        name=server.name,
        embed=embed,
        view=view_feedback_card
    )

    view_server_card = discord.ui.View().add_item(
        discord.ui.Button(emoji='🔗', label='Отзывы сервера', url=server_feedback_channel.message.jump_url))
    await server_card.edit(embeds=server_card.embeds, view=view_server_card)

    await server_gateway.set_message_id(server.id, server_card.id)
    await server_gateway.set_forum_id(server.id, server_feedback_channel.thread.id)
    await uow.commit()


@broker.subscriber("add_pvp_server")
@inject
async def add_pvp_server_handle(server: CreateServerDTO, config: FromDishka[BotConfig]):
    async with container() as request_container:
        pvp_server_gateway: IPVPServerGateway = await request_container.get(IPVPServerGateway)
        uow: IUoW = await request_container.get(IUoW)
        await add_server_process(pvp_server_gateway, uow, server, config.pvp_channel_embeds_id,
                                 config.pvp_forum_feedback_id)


@broker.subscriber("add_pve_server")
@inject
async def add_pve_server_handle(server: CreateServerDTO, config: FromDishka[BotConfig]):
    async with container() as request_container:
        pve_server_gateway: IPVEServerGateway = await request_container.get(IPVEServerGateway)
        uow: IUoW = await request_container.get(IUoW)
        await add_server_process(pve_server_gateway, uow, server, config.pve_channel_embeds_id,
                                 config.pve_forum_feedback_id)


async def delete_server_process(server: ServerDTO, channel_embeds_id, forum_feedback_id):
    message = await get_message_by_message_id(bot, channel_embeds_id, server.message_id)
    feedback_channel = get_forum_channel_by_name(bot, forum_feedback_id, server.name)
    await message.delete()
    await feedback_channel.delete()


@broker.subscriber("delete_pvp_server")
@inject
async def delete_pvp_server_handle(server: ServerDTO, config: FromDishka[BotConfig]) -> None:
    await delete_server_process(server, config.pvp_channel_embeds_id, config.pvp_forum_feedback_id)


@broker.subscriber("delete_pve_server")
@inject
async def delete_pve_server_handle(server: ServerDTO, config: FromDishka[BotConfig]) -> None:
    await delete_server_process(server, config.pve_channel_embeds_id, config.pve_forum_feedback_id)


@bot.event
async def on_ready():
    logger.info('Bot started')
    update_server_banners.start()
    update_server_top.start()
    await broker.start()


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    user = payload.member

    if payload.channel_id not in [config.bot_config.pvp_channel_embeds_id,
                                  config.bot_config.pve_channel_embeds_id] or user.bot:
        return

    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

    reactions_counts = 0
    for reaction in message.reactions:
        async for reaction_user in reaction.users():
            if user == reaction_user:
                reactions_counts += 1
                if reactions_counts > 1:
                    await reaction.remove(user)


@bot.event
async def on_member_join(member: Member) -> None:
    message_author = await get_user_by_id(
        bot=bot,
        user_id=config.bot_config.guildmaster_id
    )
    invite_code = config.bot_config.server_invite_code
    embed = discord.Embed(
        description="""
            Приветствую тебя любитель DayZ RP!
            Я KOLOV !
            Я рад приветствовать тебя на нашем замечательном камьюнити, которое создано специально, что бы тебе было проще найти себе проект по душе!
            На нашем камьюнити добавлена система оценок и отзывов, ты можешь выбрать себе проект основываясь на них, а так же и сам оценить какой либо из проектов!
            У нас представлены самые разные проекты как по тематике Сталкера, или как тебе например РП сервер по тематике The Elder Scrolls: Skyrim!?
            Будь как дома, выбирай просто и без долгих поисков!
        """,
        color=discord.Color.green()
    )
    embed.set_author(
        name=message_author.display_name,
        icon_url=message_author.avatar.url
    )
    button = discord.ui.Button(
        label='На сервер',
        style=ButtonStyle.link,
        url=f'https://discord.gg/{invite_code}',
        emoji='🔗'
    )
    try:
        await member.send(embed=embed, view=discord.ui.View().add_item(button))
    except discord.Forbidden:
        logging.exception(f'Error sending private message to {member}')


@tasks.loop(minutes=config.bot_config.task_update_minute)
async def update_server_banners():
    logger.info('Start embeds update')

    async with container() as request_container:
        pvp_server_gateway: IPVPServerGateway = await request_container.get(IPVPServerGateway)
        pve_server_gateway: IPVEServerGateway = await request_container.get(IPVEServerGateway)
        await update_embeds_service(
            bot=bot,
            channel_id=config.bot_config.pvp_channel_embeds_id,
            server_gateway=pvp_server_gateway
        )
        await update_embeds_service(
            bot=bot,
            channel_id=config.bot_config.pve_channel_embeds_id,
            server_gateway=pve_server_gateway
        )


@tasks.loop(hours=config.bot_config.top_update_hours)
async def update_server_top():
    moscow_tz = pytz.timezone('Europe/Moscow')
    date = datetime.now(tz=moscow_tz)
    if date.day != config.bot_config.number_day_update_top:
        return

    async with container() as request_container:
        pvp_server_gateway: IPVPServerGateway = await request_container.get(IPVPServerGateway)
        pve_server_gateway: IPVPServerGateway = await request_container.get(IPVEServerGateway)
        logger.info('Start update server top')
        await asyncio.gather(
            update_top(
                server_gateway=pve_server_gateway,
                bot=bot,
                embed_channel_id=config.bot_config.pve_channel_embeds_id,
                top_channel_id=config.bot_config.pve_channel_top_id,
                required_reaction_count=config.bot_config.pve_required_reaction_count,
                placing_count=config.bot_config.placing_top_count,
                type='pve',
            ),
            update_top(
                server_gateway=pvp_server_gateway,
                bot=bot,
                embed_channel_id=config.bot_config.pvp_channel_embeds_id,
                top_channel_id=config.bot_config.pvp_channel_top_id,
                required_reaction_count=config.bot_config.pvp_required_reaction_count,
                placing_count=config.bot_config.placing_top_count,
                type='pvp',
            ),
        )


@bot.tree.command(
    name='update',
    description='Запускает обновление списка серверов серверов',
)
@commands.has_permissions(administrator=True)
async def update(interaction: Interaction):
    response: InteractionResponse = interaction.response  # type: ignore
    embed = discord.Embed(
        title='✅ Начинаю обновление!',
        color=discord.Color.blue()
    )
    async with container() as request_container:
        pvp_server_gateway: IPVPServerGateway = await request_container.get(IPVPServerGateway)
        pve_server_gateway: IPVPServerGateway = await request_container.get(IPVEServerGateway)

        await response.send_message(  # type: ignore
            embed=embed,
            ephemeral=True
        )

        await update_embeds_service(
            bot=bot,
            channel_id=config.bot_config.pvp_channel_embeds_id,
            server_gateway=pvp_server_gateway
        )

        await update_embeds_service(
            bot=bot,
            channel_id=config.bot_config.pve_channel_embeds_id,
            server_gateway=pve_server_gateway
        )


@bot.tree.command(
    name='clear_reactions',
    description='Удаляет все оценки пользователя',
    guild=discord.Object(id=config.bot_config.guild_id)
)
@commands.has_permissions(administrator=True)
async def clear_reactions(
        interaction: Interaction,
        user: User = None,
        user_id: str = None
):
    response: InteractionResponse = interaction.response  # type: ignore

    if user is None:
        if user_id is None:
            embed = discord.Embed(
                title='🛑 Не указан пользователь!',
                color=discord.Color.red()
            )
            await response.send_message(  # type: ignore
                embed=embed,
                ephemeral=True
            )
            return

        user = await get_user_by_id(
            bot=bot,
            user_id=int(user_id)
        )

    embed = discord.Embed(
        title='✅  Начинаю удаление реакций!',
        description='Отчет будет отправлен в ЛС после завершения операции. Время операции может занять более 5 минут',
        color=discord.Color.blue()
    )
    await response.send_message(  # type: ignore
        embed=embed,
        ephemeral=True,
    )

    logs_embed = await clear_user_reactions(
        bot=bot,
        id_channel=config.bot_config.pvp_channel_embeds_id,
        user=user
    )
    try:
        await interaction.user.send(
            embed=logs_embed
        )
    except discord.Forbidden as e:
        logger.exception(f'Ошибка отправки сообщения для {interaction.user}: {str(e)}')


def main() -> None:
    global container

    logger.info("Initializing DI")
    container = make_async_container(
        DbProvider(),
        GatewaysProvider(),
        context={
            APIConfig: APIConfig(),
            BotConfig: BotConfig(),
            BrokerConfig: BrokerConfig(),
            StorageConfig: StorageConfig(),
            DBConfig: DBConfig(),
        }
    )
    setup_dishka(container, app)

    logger.info("Initializing bot")

    bot.run(config.bot_config.bot_token)
    print("Bot")


if __name__ == "__main__":
    main()
