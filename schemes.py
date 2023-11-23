from dataclasses import dataclass


@dataclass
class ServerInfo:
    name: str
    address: str
    query_port: int
    port: int
    mode: str
    registration_type: str
    description: str
    invite_code: str
    banner_url: str
    message_id: int | None = None


@dataclass
class ServerBannerInfo:
    status: str
    players: int
    max_players: int
    version: str
    map: str
