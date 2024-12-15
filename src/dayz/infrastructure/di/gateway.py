from dishka import Provider, Scope, provide

from dayz.application.interfaces.server import IPVPServerGateway, IPVEServerGateway
from dayz.application.interfaces.user import IUserGateway
from dayz.infrastructure.db.gateways.server import PVEServerGateway, PVPServerGateway
from dayz.infrastructure.db.gateways.user import UserGateway


class GatewaysProvider(Provider):
    scope = Scope.REQUEST

    user_gateway = provide(
        source=UserGateway,
        provides=IUserGateway
    )

    pvp_server_gateway = provide(
        source=PVPServerGateway,
        provides=IPVPServerGateway
    )

    pve_server_gateway = provide(
        source=PVEServerGateway,
        provides=IPVEServerGateway
    )
