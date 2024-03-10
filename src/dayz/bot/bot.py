import logging
import tracemalloc
from datetime import datetime

import discord
from discord import RawReactionActionEvent, Interaction, InteractionResponse, NotFound, Member, ButtonStyle
from discord.ext import commands, tasks

from dayz import settings
from dayz.application.models.server import ServerEmbedData, ServerData
from dayz.bot.forms import ServerInfoInput
from dayz.bot.service.server import get_embed, add_server, delete_server, update_embeds_service, update_top
from dayz.bot.utils.bot import get_server_icon, get_member_by_id
from dayz.settings import CHANNEL_EMBEDS_ID

logger = logging.getLogger(__name__)

bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all()
)


@bot.tree.command(name='create',
                  description='Добавляет новый банер в список серверов',
                  guild=discord.Object(id=settings.GUILD_ID)
                  )
@commands.has_permissions(administrator=True)
async def create(
        interaction: Interaction,
        name: str,
        invite_code: str
):
    response: InteractionResponse = interaction.response  # type: ignore
    if not interaction.user.guild_permissions.administrator:
        await response.send_message(
            content='Недостаточно прав',
            ephemeral=True
        )

        return

    server_input_modal = ServerInfoInput()
    await response.send_modal(server_input_modal)
    await server_input_modal.wait()

    address, port, query_port = server_input_modal.address.value.split(':')

    server_info = ServerData(
        name=name,
        invite_code=invite_code,
        address=address,
        port=port,
        query_port=query_port,
        mode=server_input_modal.mode.value,
        registration_type=server_input_modal.registration_type.value,
        banner_url=server_input_modal.image_url.value,
        description=server_input_modal.description.value,
    )

    server_data = ServerEmbedData(
        avatar_url=bot.user.avatar.url,
        data=server_info
    )

    embed = await get_embed(server_data)
    message = await interaction.channel.send(embed=embed)
    try:
        server_info.message_id = message.id
        add_server(server_info)
    except Exception as e:
        await message.delete()
        logger.exception(f"Can't save server to database {e}")
        print(f'Error {e}')
        return

    for i in range(1, 6):
        emoji = f'{i}\u20e3'  # Получаем соответствующий эмодзи
        await message.add_reaction(emoji)


@tasks.loop(minutes=settings.TASK_UPDATE_MINUTE)
async def update_server_banners():
    logger.info('Start embeds update')
    await update_embeds_service(
        bot=bot,
        channel_id=CHANNEL_EMBEDS_ID
    )


@tasks.loop(hours=settings.TOP_UPDATE_HOURS)
async def update_server_top():
    date = datetime.now()
    if date.day != settings.NUMBER_DAY_UPDATE_TOP:
        return

    logger.info('Start update server top')
    await update_top(
        bot=bot,
        embed_channel_id=settings.CHANNEL_EMBEDS_ID,
        top_channel_id=settings.CHANNEL_TOP_ID,
        required_reaction_count=settings.REQUIRED_REACTION_COUNT,
        placing_count=settings.PLACING_TOP_COUNT
    )


@bot.event
async def on_ready() -> None:
    synced = await bot.tree.sync(guild=discord.Object(id=settings.GUILD_ID))
    update_server_banners.start()
    update_server_top.start()
    logger.info(f'Bot {bot.user.name} started with {len(synced)} commands.')


@bot.tree.command(
    name='update',
    description='Запускает обновление списка серверов серверов',
    guild=discord.Object(id=settings.GUILD_ID)
)
@commands.has_permissions(administrator=True)
async def update(interaction: Interaction):
    response: InteractionResponse = interaction.response  # type: ignore
    embed = discord.Embed(
        title='✅ Начинаю обновление!',
        color=discord.Color.blue()
    )

    await response.send_message(
        embed=embed,
        ephemeral=True
    )
    await update_embeds_service(bot, settings.CHANNEL_EMBEDS_ID)


@bot.tree.command(
    name='delete',
    description='Удаляет банер из списка серверов',
    guild=discord.Object(id=settings.GUILD_ID)
)
@commands.has_permissions(administrator=True)
async def delete(
        interaction: Interaction,
        message_id: str
) -> None:
    response: InteractionResponse = interaction.response  # type: ignore
    message_id = int(message_id)
    delete_server(message_id)

    try:
        message = await interaction.channel.fetch_message(message_id)
        await message.delete()
        embed = discord.Embed(
            title='✅ Успех!',
            color=discord.Color.green()
        )
    except NotFound as e:
        embed = discord.Embed(
            title='🛑 Ошибка!',
            description=e.text,
            color=discord.Color.red()
        )

    await response.send_message(
        embed=embed,
        ephemeral=True
    )


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent) -> None:
    user = payload.member

    if payload.channel_id != settings.CHANNEL_EMBEDS_ID or user.bot:
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
    message_author = await get_member_by_id(
        bot=bot,
        user_id=settings.GUILDMASTER_ID
    )
    invite_code = settings.SERVER_INVITE_CODE
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


tracemalloc.start()
bot.run(settings.BOT_TOKEN)
