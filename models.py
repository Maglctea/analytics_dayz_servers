from dataclasses import dataclass


@dataclass
class Server:
    status: str
    address: str
    port: int
    version: str
    map: str
    players: int
    max_players: int