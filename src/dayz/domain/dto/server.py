from dataclasses import dataclass


@dataclass
class BaseServerDTO:
    id: int
    name: str
    address: str
    port: int
    query_port: int | None
    mode: str
    registration_type: str
    description: str
    invite_code: str
    banner_url: str


@dataclass
class ServerDTO(BaseServerDTO):
    message_id: int | None = None
    forum_id: int | None = None


@dataclass
class CreateServerDTO(BaseServerDTO):
    ...


@dataclass
class ServerEmbedDTO:
    avatar_url: str
    data: CreateServerDTO


@dataclass
class ServerBannerInfoDTO:
    status: str
    players: int
    max_players: int
    version: str
    map: str
