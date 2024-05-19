from typing import Protocol

from dayz.domain.dto.server import ServerDTO, CreateServerDTO


class IServerGateway(Protocol):
    def add_server(self, server: CreateServerDTO) -> ServerDTO:
        raise NotImplementedError

    async def update_server(
            self,
            server: ServerDTO,
            values: dict
    ):
        raise NotImplementedError

    async def get_server(
            self,
            message_id: int = None,
            name: str = None
    ) -> ServerDTO | None:
        raise NotImplementedError

    async def get_servers(self) -> list[ServerDTO]:
        raise NotImplementedError

    async def delete_server(self, message_id: int) -> None:
        raise NotImplementedError

    async def set_message_id(self, server_id: int, message_id: int) -> None:
        raise NotImplementedError

    async def set_forum_id(self, server_id: int, forum_id: int) -> None:
        raise NotImplementedError
