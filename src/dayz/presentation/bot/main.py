import asyncio
import logging
import os
import sys
from datetime import datetime

import discord
from discord import Interaction, User, ButtonStyle, Member
from discord.ext import commands, tasks
from dishka import make_async_container, AsyncContainer
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from dayz.application.interfaces.server import IServerGateway
from dayz.application.interfaces.uow import IUoW
from dayz.domain.dto.configs.bot import BotConfig
from dayz.domain.dto.configs.db import DBConfig
from dayz.domain.dto.server import ServerEmbedDTO, ServerDTO, CreateServerDTO
from dayz.infrastructure.config_loader import load_config
from dayz.infrastructure.di.config import BotConfigProvider
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
broker = RabbitBroker(url=os.getenv('RABBITMQ_HOST'))
app = FastStream(broker)

db_config = load_config(
    config_type=DBConfig,
    config_scope='db',
)

bot_config = load_config(
    config_type=BotConfig,
    config_scope='bot',
)


@broker.subscriber("add_server")  # handle messages by routing key
async def add_server_handle(server: CreateServerDTO):
    server_data = ServerEmbedDTO(
        avatar_url=bot.user.avatar.url,
        data=server
    )

    embed = await get_embed(server_data)
    channel = bot.get_channel(bot_config.channel_embeds_id)

    server_card = await channel.send(embed=embed)

    for i in range(1, 6):
        emoji = f'{i}\u20e3'  # Получаем соответствующий эмодзи
        await server_card.add_reaction(emoji)

    forum: discord.ForumChannel = bot.get_channel(bot_config.forum_feedback_id)

    embed = discord.Embed(
        title=server.name,
        description=f'Тут вы можете оставить отзыв или посмотреть информацию о сервере {server.name}'
    )
    view_feedback_card = discord.ui.View().add_item(discord.ui.Button(emoji='🔗', label='Карточка сервера', url=server_card.jump_url))

    server_feedback_channel = await forum.create_thread(
        name=server.name,
        embed=embed,
        view=view_feedback_card
    )

    view_server_card = discord.ui.View().add_item(discord.ui.Button(emoji='🔗', label='Отзывы сервера', url=server_feedback_channel.message.jump_url))
    await server_card.edit(embeds=server_card.embeds, view=view_server_card)

    async with container() as request_container:
        server_gateway: IServerGateway = await request_container.get(IServerGateway)
        uow: IUoW = await request_container.get(IUoW)
        await server_gateway.set_message_id(server.id, server_card.id)
        await server_gateway.set_forum_id(server.id, server_feedback_channel.thread.id)
        await uow.commit()


@broker.subscriber("delete_server")  # handle messages by routing key
async def delete_server_handle(server: ServerDTO) -> None:
    message = await get_message_by_message_id(bot, bot_config.channel_embeds_id, server.message_id)
    feedback_channel = get_forum_channel_by_name(bot, bot_config.forum_feedback_id, server.name)
    await message.delete()
    await feedback_channel.delete()


@bot.event
async def on_ready():
    logger.info('Bot started')
    await broker.start()
    update_server_banners.start()
    update_server_top.start()


@bot.event
async def on_member_join(member: Member) -> None:
    message_author = await get_user_by_id(
        bot=bot,
        user_id=bot_config.guildmaster_id
    )
    invite_code = bot_config.server_invite_code
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


@tasks.loop(minutes=bot_config.task_update_minute)
async def update_server_banners():
    logger.info('Start embeds update')

    async with container() as request_container:
        server_gateway: IServerGateway = await request_container.get(IServerGateway)
        await update_embeds_service(
            bot=bot,
            channel_id=bot_config.channel_embeds_id,
            server_gateway=server_gateway
        )


@tasks.loop(hours=bot_config.top_update_hours)
async def update_server_top():
    date = datetime.now()
    if date.day != bot_config.number_day_update_top:
        return

    async with container() as request_container:
        server_gateway: IServerGateway = await request_container.get(IServerGateway)
        logger.info('Start update server top')
        await update_top(
            server_gateway=server_gateway,
            bot=bot,
            embed_channel_id=bot_config.channel_embeds_id,
            top_channel_id=bot_config.channel_top_id,
            required_reaction_count=bot_config.required_reaction_count,
            placing_count=bot_config.placing_top_count
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
        server_gateway: IServerGateway = await request_container.get(IServerGateway)

        await response.send_message(  # type: ignore
            embed=embed,
            ephemeral=True
        )

        await update_embeds_service(
            bot=bot,
            channel_id=bot_config.channel_embeds_id,
            server_gateway=server_gateway
        )


@bot.tree.command(
    name='clear_reactions',
    description='Удаляет все оценки пользователя',
    guild=discord.Object(id=bot_config.guild_id)
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
        id_channel=bot_config.channel_embeds_id,
        user=user
    )
    try:
        await interaction.user.send(
            embed=logs_embed
        )
    except discord.Forbidden as e:
        logger.exception(f'Ошибка отправки сообщения для {interaction.user}: {str(e)}')


async def run_bot(config: BotConfig):
    await bot.start(config.bot_token)


async def main() -> None:
    global container

    logger.info("Initializing DI")
    container = make_async_container(
        BotConfigProvider(),
        DbProvider(config=db_config),
        GatewaysProvider(),
    )

    logger.info("Initializing bot")
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)

    await run_bot(bot_config)
    print("Bot")


if __name__ == "__main__":
    asyncio.run(main())
