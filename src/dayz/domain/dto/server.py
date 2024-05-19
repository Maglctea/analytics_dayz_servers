from dataclasses import dataclass, field


@dataclass
class ServerDTO:
    id: int
    name: str
    address: str
    port: int
    query_port: int
    mode: str
    registration_type: str
    description: str
    invite_code: str
    banner_url: str
    message_id: int
    forum_id: int


@dataclass
class CreateServerDTO:
    id: int
    name: str
    address: str
    port: int
    query_port: int
    mode: str
    registration_type: str
    description: str
    invite_code: str
    banner_url: str



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
