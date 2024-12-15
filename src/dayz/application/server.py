from dayz.application.interfaces.server import IPVPServerGateway
from dayz.application.interfaces.uow import IUoW
from dayz.domain.dto.server import ServerDTO, CreateServerDTO


class CreateServerInteractor:
    def __init__(
            self,
            unit_of_work: IUoW,
            server_gateway: IPVPServerGateway,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.server_gateway = server_gateway

    async def __call__(
            self,
            created_server: CreateServerDTO
    ) -> ServerDTO:
        created_server = self.server_gateway.add_server(
            server=created_server
        )

        await self.unit_of_work.commit()
        return created_server
