import discord
from discord import ui


class ServerInfoInput(ui.Modal, title='Questionnaire Response'):
    address = ui.TextInput(
        label='IP адрес:порт:Query port',
        placeholder='127.0.0.1:2302:2305'
    )
    mode = ui.TextInput(
        label='Режим игры',
        placeholder='Hard RP'
    )
    registration_type = ui.TextInput(
        label='Вид регистрации',
        placeholder='Анкета + Whitelist'
    )
    image_url = ui.TextInput(
        label='URL картинки банера',
        placeholder='https://link-to-photo.png'
    )
    description = ui.TextInput(
        label='Описание сервера',
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
