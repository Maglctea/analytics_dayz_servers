from .admin import AdminConfig
from .api import APIConfig
from .auth import AuthConfig
from .bot import BotConfig
from .db import DBConfig
from .broker import BrokerConfig
from .storage import StorageConfig

admin_config = AdminConfig()
api_config = APIConfig()
auth_config = AuthConfig()
bot_config = BotConfig()
db_config = DBConfig()
broker_config = BrokerConfig()
storage_config = StorageConfig()
