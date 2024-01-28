from environs import Env

env = Env()
env.read_env()

# Bot
CHANNEL_EMBEDS_ID = env.int('CHANNEL_EMBEDS_ID', None)
CHANNEL_TOP_ID = env.int('CHANNEL_TOP_ID', None)
GUILD_ID = env.int('GUILD_ID', None)
TASK_UPDATE_MINUTE = env.int('TASK_UPDATE_MINUTE', None)
TOP_UPDATE_HOURS = env.int('TOP_UPDATE_HOURS', None)
BOT_TOKEN = env('BOT_TOKEN', None)
SERVER_INVITE_CODE = env('SERVER_INVITE_CODE', None)

# Database
DATABASE_URL = env('DATABASE_URL', None)

# Admin panel
ADMIN_PANEL_SECRET_KEY = env('ADMIN_PANEL_SECRET_KEY', None)
