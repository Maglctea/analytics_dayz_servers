from sqlalchemy import Text, BIGINT
from sqlalchemy.orm import Mapped, mapped_column, registry

from dayz.infrastructure.db.models.base import BaseModel

mapper_registry = registry()


class PVPServer(BaseModel):
    __tablename__ = 'pvp_servers'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]
    port: Mapped[int]
    query_port: Mapped[int | None]
    mode: Mapped[str]
    registration_type: Mapped[str]
    description: Mapped[str] = mapped_column(Text())
    invite_code: Mapped[str]
    banner_url: Mapped[str]
    message_id: Mapped[int | None] = mapped_column(BIGINT(), nullable=True)
    forum_id: Mapped[int | None] = mapped_column(BIGINT(), nullable=True)

    def __str__(self):
        return self.name


class PVEServer(BaseModel):
    __tablename__ = 'pve_servers'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]
    port: Mapped[int]
    query_port: Mapped[int | None]
    mode: Mapped[str]
    registration_type: Mapped[str]
    description: Mapped[str] = mapped_column(Text())
    invite_code: Mapped[str]
    banner_url: Mapped[str]
    message_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)
    forum_id: Mapped[int] = mapped_column(BIGINT(), nullable=True)

    def __str__(self):
        return self.name
