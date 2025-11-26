from dishka import Provider, Scope, from_context

from dayz.config import (
    APIConfig,
    AuthConfig, DBConfig,
)
from dayz.config import BrokerConfig
from dayz.config.admin import AdminConfig
from dayz.config.bot import BotConfig
from dayz.config.storage import StorageConfig


class ConfigProvider(Provider):
    scope = Scope.APP

    admin_config = from_context(AdminConfig)
    api_config = from_context(APIConfig)
    auth_config = from_context(AuthConfig)
    bot_config = from_context(BotConfig)
    broker_config = from_context(BrokerConfig)
    storage_config = from_context(StorageConfig)
    db_config = from_context(DBConfig)
