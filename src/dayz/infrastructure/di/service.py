from dishka import Provider, provide

from dayz.infrastructure.auth.access import JWTGetUserService


class ServiceProvider(Provider):
    access = provide(JWTGetUserService)
