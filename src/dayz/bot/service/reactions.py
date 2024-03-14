import discord
from discord import User, Embed
from discord.ext.commands import Bot

from dayz.bot.utils.bot import get_messages


async def clear_user_reactions(
        bot: Bot,
        id_channel: int,
        user: User,
) -> Embed:
    logs = f'**Удалены следующие оценки:**\n{"=" * 30}\n'
    count_reactions = 0

    async for message in await get_messages(bot, id_channel):
        for reaction in message.reactions:

            if user in [current_user async for current_user in reaction.users()]:
                try:
                    await reaction.remove(user)
                    logs += f"- {reaction.emoji} из **{message.embeds[0].title}**\n"
                    count_reactions += 1
                except Exception as e:
                    logs += f"🛑 Ошибка удаления {reaction.emoji} из сервера **{message.embeds[0].title}**! Причина: *{str(e)}*\n"

    embed = Embed(
        title='✅ Задача завершена',
        description=logs,
        color=discord.Color.green()
    )
    embed.add_field(
        name='Оценки сняты с:',
        value=user.mention
    )
    embed.add_field(
        name='Количество удаленных оценок:',
        value=count_reactions
    )

    return embed
