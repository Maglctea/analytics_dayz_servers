from dishka import Provider, Scope, provide

from dayz.application.interfaces.server import IPVPServerGateway
from dayz.application.interfaces.user import IUserGateway
from dayz.infrastructure.db.gateways.server import PVEServerGateway
from dayz.infrastructure.db.gateways.user import UserGateway


class GatewaysProvider(Provider):
    scope = Scope.REQUEST

    user_gateway = provide(
        source=UserGateway,
        provides=IUserGateway
    )

    server_gateway = provide(
        source=PVEServerGateway,
        provides=IPVPServerGateway
    )
