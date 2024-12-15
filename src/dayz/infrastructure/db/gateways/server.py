from adaptix import Retort
from sqlalchemy import or_
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from dayz.application.interfaces.server import IServerGateway, IPVEServerGateway
from dayz.domain.dto.server import ServerDTO
from dayz.infrastructure.db.converter import model_to_server_converter
from dayz.infrastructure.db.models import PVPServer, PVEServer

retort = Retort()


class PVPServerGateway(IServerGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_server(
            self,
            message_id: int = None,
            name: str = None
    ) -> ServerDTO | None:
        stmt = (
            select(PVPServer)
            .filter(
                or_(
                    PVPServer.message_id == message_id,
                    PVPServer.name == name
                )
            )
        )
        server_scalar = await self.session.scalar(stmt)
        if server_scalar:
            return model_to_server_converter(server_scalar)
        return None

    async def get_server_by_id(
            self,
            server_id: int = None,
    ) -> ServerDTO | None:
        server = await self.session.get_one(PVPServer, server_id)
        return model_to_server_converter(server)

    async def get_servers(self) -> list[ServerDTO]:
        stmt = select(PVPServer)
        servers_scalar = list(await self.session.scalars(stmt))

        servers = [
            model_to_server_converter(server_scalar)
            for server_scalar in servers_scalar
        ]
        return servers

    async def delete_server(
            self,
            message_id: int
    ):
        stmt = delete(PVPServer).where(PVPServer.message_id == message_id)
        await self.session.execute(stmt)

    async def set_message_id(self, server_id: int, message_id: int) -> None:
        stmt = (
            update(PVPServer)
            .where(PVPServer.id == server_id)
            .values({'message_id': message_id})
        )
        await self.session.execute(stmt)

    async def set_forum_id(self, server_id: int, forum_id: int) -> None:
        stmt = (
            update(PVPServer)
            .where(PVPServer.id == server_id)
            .values({'forum_id': forum_id})
        )
        await self.session.execute(stmt)


class PVEServerGateway(IPVEServerGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_server(
            self,
            message_id: int = None,
            name: str = None
    ) -> ServerDTO | None:
        stmt = (
            select(PVEServer)
            .filter(
                or_(
                    PVEServer.message_id == message_id,
                    PVEServer.name == name
                )
            )
        )
        server_scalar = await self.session.scalar(stmt)
        if server_scalar:
            return model_to_server_converter(server_scalar)
        return None

    async def get_server_by_id(
            self,
            server_id: int = None,
    ) -> ServerDTO | None:
        server = await self.session.get_one(PVEServer, server_id)
        return model_to_server_converter(server)

    async def get_servers(self) -> list[ServerDTO]:
        stmt = select(PVEServer)
        servers_scalar = list(await self.session.scalars(stmt))

        servers = [
            model_to_server_converter(server_scalar)
            for server_scalar in servers_scalar
        ]
        return servers

    async def delete_server(
            self,
            message_id: int
    ):
        stmt = delete(PVEServer).where(PVEServer.message_id == message_id)
        await self.session.execute(stmt)

    async def set_message_id(self, server_id: int, message_id: int) -> None:
        stmt = (
            update(PVEServer)
            .where(PVEServer.id == server_id)
            .values({'message_id': message_id})
        )
        await self.session.execute(stmt)

    async def set_forum_id(self, server_id: int, forum_id: int) -> None:
        stmt = (
            update(PVEServer)
            .where(PVEServer.id == server_id)
            .values({'forum_id': forum_id})
        )
        await self.session.execute(stmt)
