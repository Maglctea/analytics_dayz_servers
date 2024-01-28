from dataclasses import dataclass, field


@dataclass
class ServerData:
    name: str
    address: str
    port: int
    query_port: int
    mode: str
    registration_type: str
    description: str
    invite_code: str
    banner_url: str
    message_id: int | None = field(kw_only=True, default=None)
    id: int | None = None


@dataclass
class ServerEmbedData:
    avatar_url: str
    data: ServerData


@dataclass
class ServerBannerInfo:
    status: str
    players: int
    max_players: int
    version: str
    map: str
