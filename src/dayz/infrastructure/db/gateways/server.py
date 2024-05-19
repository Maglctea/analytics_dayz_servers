import asyncio

from adaptix import Retort
from sqlalchemy import or_
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from dayz.domain.dto.server import ServerDTO, CreateServerDTO
from dayz.infrastructure.db.converter import model_to_server_converter
from dayz.infrastructure.db.core import create_engine, create_session_factory
from dayz.infrastructure.db.models import Server

retort = Retort()


class ServerGateway:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def update_server(
            self,
            server: ServerDTO,
            values: dict
    ):
        stmt = (
            update(Server)
            .where(Server.name == server.name)
            .values(values)
        )

        await self.session.execute(stmt)

    async def get_server(
            self,
            message_id: int = None,
            name: str = None
    ) -> ServerDTO | None:
        stmt = (
            select(Server)
            .filter(
                or_(
                    Server.message_id == message_id,
                    Server.name == name
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
        server = await self.session.get_one(Server, server_id)
        return model_to_server_converter(server)

    async def get_servers(self) -> list[ServerDTO]:
        stmt = select(Server)
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
        stmt = delete(Server).where(Server.message_id == message_id)
        await self.session.execute(stmt)

    async def set_message_id(self, server_id: int, message_id: int) -> None:
        stmt = (
            update(Server)
            .where(Server.id == server_id)
            .values({'message_id': message_id})
        )
        await self.session.execute(stmt)

    async def set_forum_id(self, server_id: int, forum_id: int) -> None:
        stmt = (
            update(Server)
            .where(Server.id == server_id)
            .values({'forum_id': forum_id})
        )
        await self.session.execute(stmt)


# async def m():
#     engine = create_engine(
#                 full_url='postgresql+asyncpg://admin:dayzadmin_4632@45.80.71.140:5433/dayz',
#                 echo=True
#             )
#
#     session_factory = create_session_factory(engine)
#
#     async with session_factory() as session:
#         gate = ServerGateway(session)
#         server = await gate.get_server_by_id(1)
#         print(server)
#         await gate.set_message_id(77, 123)
#         await gate.set_forum_id(77, 123)
#         await session.commit()
#
# asyncio.run(m())
# server = CreateServerDTO(
#     name='test',
#     address='127.0.0.1',
#     port=213,
#     query_port=5432,
#     mode='test mode',
#     registration_type='my_type',
#     description='test description',
#     invite_code='dfsdfcsdf',
#     banner_url='https/test.ru',
#     message_id=123213,
#     forum_id=123123
# )
# # model_to_dto = get_converter(Server, CreateServerDTO)
# dto_to_model = get_converter(CreateServerDTO, Server, recipe=[allow_unlinked_optional('id')])
# # server_dto = model_to_dto(server)
# server_model = dto_to_model(server)
#
# pass
