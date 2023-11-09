import discord
from discord import RawReactionActionEvent, ui, Interaction
from discord.ext import commands, tasks
from discord.ext.commands import Context

from settings import CHANNEL_EMBEDS_ID, TASK_UPDATE_MINUTE, GUILD_ID, BOT_TOKEN
from utils.bot import bulid_embed, update_embeds, get_message_by_id, get_rating
from utils.parser import get_pages, parse_page

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


class ServerInfoInput(ui.Modal, title='Questionnaire Response'):
    invite_code = ui.TextInput(label='Инвайт код', placeholder='yqhX77nt')
    mode = ui.TextInput(label='Режим игры', placeholder='Hard RP')
    registration_type = ui.TextInput(label='Вид регистрации', placeholder='Анкета + Whitelist')
    image_url = ui.TextInput(label='URL картинки банера', placeholder='https://link-to-photo.png')
    description = ui.TextInput(label='Описание сервера', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


@bot.tree.command(name='create', description='Добавляет новый сервер в список серверов',
                  guild=discord.Object(id=GUILD_ID))
@commands.has_permissions(administrator=True)
async def create(interaction: Interaction, id_server: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('Недостаточно прав', ephemeral=True)
        return

    server_info = ServerInfoInput()
    await interaction.response.send_modal(server_info)
    await server_info.wait()

    pages = await get_pages([int(id_server)])
    server = parse_page(pages[0])

    embed = await bulid_embed(
        invite_code=server_info.invite_code.value,
        server_info=server,
        registration=server_info.registration_type.value,
        mode=server_info.mode.value,
        rating=0,
        bot_icon=bot.user.display_avatar.url,
        description=server_info.description.value,
        banner_url=server_info.image_url.value
    )

    message = await interaction.channel.send(embed=embed)

    for i in range(1, 6):
        emoji = f'{i}\u20e3'  # Получаем соответствующий эмодзи
        await message.add_reaction(emoji)


@bot.tree.command(name='update', description='Добавляет новый сервер в список серверов',
                  guild=discord.Object(id=GUILD_ID))
@commands.has_permissions(administrator=True)
async def update(interaction: Interaction, id_server: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message('Недостаточно прав', ephemeral=True)
        return

    message = await get_message_by_id(bot, CHANNEL_EMBEDS_ID, id_server)

    if message is None:
        await interaction.response.send_message('Сервер с данным ID не найден', ephemeral=True)
        return

    server_info = ServerInfoInput()
    await interaction.response.send_modal(server_info)
    await server_info.wait()

    pages = await get_pages([int(id_server)])
    server = parse_page(pages[0])

    message_embed = message.embeds[0]
    fields = message_embed.fields

    embed = await bulid_embed(
        invite_code=server_info.invite_code.value if server_info.invite_code.value != '*' else message_embed.author.url,
        server_info=server,
        registration=server_info.registration_type.value if server_info.registration_type.value != '*' else fields[
            0].value,
        mode=server_info.mode.value if server_info.mode.value != '*' else fields[1].value,
        rating=await get_rating(message),
        bot_icon=bot.user.display_avatar.url,
        description=server_info.description.value if server_info.description.value != '*' else message_embed.description,
        banner_url=server_info.image_url.value if server_info.image_url.value != '*' else message_embed.image.url
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


bot.run(BOT_TOKEN)
