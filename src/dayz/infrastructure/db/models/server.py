from sqlalchemy import Text, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, registry

from dayz.domain.dto.server import ServerDTO
from dayz.infrastructure.db.models.base import BaseModel

mapper_registry = registry()


class Server(BaseModel):
    __tablename__ = 'servers'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]
    port: Mapped[int]
    query_port: Mapped[int]
    mode: Mapped[str]
    registration_type: Mapped[str]
    description: Mapped[str] = mapped_column(Text())
    invite_code: Mapped[str]
    banner_url: Mapped[str]
    message_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)
    forum_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)

    def __str__(self):
        return self.name
