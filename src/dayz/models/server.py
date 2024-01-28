from sqlalchemy import Text, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, registry

from dayz.application.models.server import ServerData
from dayz.models.base import BaseModel

mapper_registry = registry()


class ServerModel(BaseModel):
    __tablename__ = 'servers'

    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]
    port: Mapped[int]
    query_port: Mapped[int]
    mode: Mapped[str]
    registration_type: Mapped[str]
    description: Mapped[Text] = mapped_column(Text())
    invite_code: Mapped[str]
    banner_url: Mapped[str]
    message_id: Mapped[int] = mapped_column(BIGINT())

    def __str__(self):
        return self.name

    def to_dataclass(self) -> ServerData:
        return ServerData(
            id=self.id,
            name=self.name,
            address=self.address,
            port=self.port,
            query_port=self.query_port,
            mode=self.mode,
            registration_type=self.registration_type,
            description=self.description,
            invite_code=self.invite_code,
            banner_url=self.banner_url,
            message_id=self.message_id
        )

    @staticmethod
    def to_model(server: ServerData) -> 'ServerModel':
        return ServerModel(
            name=server.name,
            address=server.address,
            port=server.port,
            query_port=server.query_port,
            mode=server.mode,
            registration_type=server.registration_type,
            description=server.description,
            invite_code=server.invite_code,
            banner_url=server.banner_url,
            message_id=server.message_id
        )
