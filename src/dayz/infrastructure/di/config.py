from dishka import Provider, Scope, provide

from dayz.domain.dto.configs.admin import AdminConfig
from dayz.domain.dto.configs.api import APIConfig
from dayz.domain.dto.configs.auth import AuthConfig
from dayz.domain.dto.configs.bot import BotConfig
from dayz.infrastructure.config_loader import load_config


class BaseConfigProvider(Provider):
    scope = Scope.APP


class APIConfigProvider(BaseConfigProvider):

    @provide
    def get_api_config(self) -> APIConfig:
        return load_config(
            config_type=APIConfig,
            config_scope='api',
        )


class AdminConfigProvider(BaseConfigProvider):
    @provide
    def get_api_config(self) -> AdminConfig:
        return load_config(
            config_type=AdminConfig,
            config_scope='admin',
        )


class AuthConfigProvider(BaseConfigProvider):
    @provide
    def get_auth_config(self) -> AuthConfig:
        return load_config(
            config_type=AuthConfig,
            config_scope='auth',
        )


class BotConfigProvider(BaseConfigProvider):
    @provide
    def get_auth_config(self) -> BotConfig:
        return load_config(
            config_type=BotConfig,
            config_scope='bot',
        )
