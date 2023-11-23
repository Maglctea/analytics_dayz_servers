import tracemalloc

import discord
from discord import RawReactionActionEvent, ui, Interaction
from discord.ext import commands, tasks
from discord.ext.commands import Context

from database.orm import add_server, get_server
from schemes import ServerInfo
from settings import CHANNEL_EMBEDS_ID, TASK_UPDATE_MINUTE, GUILD_ID, BOT_TOKEN
from utils.bot import bulid_embed, update_embeds, get_rating, get_message_by_message_id
from utils.parser import get_pages, parse_page

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


class ServerInfoInput(ui.Modal, title='Questionnaire Response'):
    address = ui.TextInput(label='IP адрес:порт:Query port', placeholder='127.0.0.1:2302:2305')
    mode = ui.TextInput(label='Режим игры', placeholder='Hard RP')
    registration_type = ui.TextInput(label='Вид регистрации', placeholder='Анкета + Whitelist')
    image_url = ui.TextInput(label='URL картинки банера', placeholder='https://link-to-photo.png')
    description = ui.TextInput(label='Описание сервера', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


@bot.tree.command(name='create', description='Добавляет новый сервер в список серверов',
                  guild=discord.Object(id=GUILD_ID))
@commands.has_permissions(administrator=True)
async def create(interaction: Interaction, name: str, invite_code: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('Недостаточно прав', ephemeral=True)
        return

    server_info = ServerInfoInput()
    await interaction.response.send_modal(server_info)
    await server_info.wait()

    address, port, query_port = server_info.address.value.split(':')

    server = ServerInfo(
        name=name,
        address=address,
        query_port=query_port,
        port=port,
        mode=server_info.mode.value,
        registration_type=server_info.registration_type.value,
        description=server_info.description.value,
        invite_code=invite_code,
        banner_url=server_info.image_url.value
    )
    add_server(server)

    pages = await get_pages([f'{address}:{query_port}'])

    server_banner_info = parse_page(pages[0])

    embed = await bulid_embed(
        server_info=server,
        server_banner_info=server_banner_info,
        rating=0,
        bot_icon=bot.user.avatar.url
    )

    message = await interaction.channel.send(embed=embed)

    for i in range(1, 6):
        emoji = f'{i}\u20e3'  # Получаем соответствующий эмодзи
        await message.add_reaction(emoji)


@bot.tree.command(name='update', description='Добавляет новый сервер в список серверов',
                  guild=discord.Object(id=GUILD_ID))
@commands.has_permissions(administrator=True)
async def update(interaction: Interaction, message_id: int, invite_code: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('Недостаточно прав', ephemeral=True)
        return

    server = get_server(message_id)

    if server is None:
        await interaction.response.send_message('Сервер с данным названием не найден', ephemeral=True)
        return

    if invite_code is not None:
        server.invite_code = invite_code

    message = await get_message_by_message_id(bot, CHANNEL_EMBEDS_ID, server.message_id)

    server_info = ServerInfoInput()

    await interaction.response.send_modal(server_info)
    await server_info.wait()

    address, port, query_port = server_info.address.value.split(':')

    new_server_info = ServerInfo(

        name=server.name,
        address=address,
        query_port=query_port,
        port=port,
        mode=server_info.mode.value,
        registration_type=server_info.registration_type.value,
        description=server_info.description.value,
        invite_code=invite_code,
        banner_url=server_info.image_url.value,
        message_id=message_id
    )

    pages = await get_pages([f'{address}:{query_port}'])
    server_banner_info = parse_page(pages[0])

    embed = await bulid_embed(
        server_info=new_server_info,
        server_banner_info=server_banner_info,
        rating=await get_rating(message),
        bot_icon=bot.user.display_avatar.url,
    )

    await message.edit(embed=embed)


@tasks.loop(minutes=TASK_UPDATE_MINUTE)
async def update_task():
    print('Start update')
    await update_embeds(bot, CHANNEL_EMBEDS_ID)


@bot.event
async def on_ready():
    synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    update_task.start()
    print(f'Синхронизировано {len(synced)} команд')
    print(f'Бот {bot.user.name} готов к работе!')


@bot.command()
async def clear(ctx: Context):
    await ctx.channel.purge()


@bot.command()
async def update(ctx: Context):
    await ctx.message.delete()
    if not ctx.author.guild_permissions.administrator:
        return
    await update_embeds(bot, CHANNEL_EMBEDS_ID)


@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    user = payload.member

    if payload.channel_id != CHANNEL_EMBEDS_ID or user.bot:
        return

    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

    reactions_counts = 0
    for reaction in message.reactions:
        async for reacrion_user in reaction.users():
            if user == reacrion_user:
                reactions_counts += 1
                if reactions_counts > 1:
                    await reaction.remove(user)


tracemalloc.start()
bot.run(BOT_TOKEN)
