from dishka import Provider, provide, Scope

from dayz.application.account.auth import BaseLoginInteractor
from dayz.application.server import CreateServerInteractor
from dayz.infrastructure.auth.access import JWTGetUserService


class AdminInteractorProvider(Provider):

    scope = Scope.REQUEST

    base_login = provide(BaseLoginInteractor)

    access = provide(JWTGetUserService)

    create_server = provide(CreateServerInteractor)
