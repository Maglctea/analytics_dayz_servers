from sqlalchemy import or_
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from src.aplication.models.server import ServerData
from src.models.server import ServerModel, to_model


class ServerGateway:
    def __init__(self, session: Session) -> None:
        self.session = session

    def commit(self) -> None:
        self.session.commit()

    def add_server(
            self,
            server: ServerData
    ) -> None:
        self.session.add(to_model(server))

    def update_server(
            self,
            server: ServerData,
            values: dict
    ):
        stmt = (
            update(ServerModel)
            .where(ServerModel.name == server.name)
            .values(values)
        )

        self.session.execute(stmt)  # .scalar_one()
        self.session.commit()

    def get_server(
            self,
            message_id: int = None,
            name: str = None
    ) -> ServerData | None:
        stmt = (
            select(ServerModel)
            .filter(
                or_(
                    ServerModel.message_id == message_id,
                    ServerModel.name == name
                )
            )
        )
        server_scalar = self.session.scalar(stmt)
        return server_scalar.to_dataclass()

    def get_servers(self) -> list[ServerData]:
        stmt = select(ServerModel)
        servers_scalar = list(self.session.scalars(stmt).all())

        servers = [
            server_scalar.to_dataclass()
            for server_scalar in servers_scalar
        ]
        return servers

    def get_top_server(
            self,
            count: int
    ) -> list[ServerData]:
        select(ServerModel)
        ...

    def delete_server(
            self,
            message_id: int
    ):
        stmt = delete(ServerModel).where(ServerModel.message_id == message_id)
        self.session.execute(stmt)
        self.session.commit()
