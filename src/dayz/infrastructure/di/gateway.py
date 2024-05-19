from dishka import Provider, Scope, provide

from dayz.application.interfaces.server import IServerGateway
from dayz.application.interfaces.user import IUserGateway
from dayz.infrastructure.db.gateways.server import ServerGateway
from dayz.infrastructure.db.gateways.user import UserGateway


class GatewaysProvider(Provider):
    scope = Scope.REQUEST

    user_gateway = provide(
        source=UserGateway,
        provides=IUserGateway
    )

    server_gateway = provide(
        source=ServerGateway,
        provides=IServerGateway
    )
