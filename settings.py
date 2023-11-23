from environs import Env

env = Env()
env.read_env()

CHANNEL_EMBEDS_ID = env.int('CHANNEL_EMBEDS_ID', None)
GUILD_ID = env.int('GUILD_ID', None)
TASK_UPDATE_MINUTE = env.int('TASK_UPDATE_MINUTE', None)
BOT_TOKEN = env('BOT_TOKEN', None)
DATABASE_URL = env('DATABASE_URL', None)
