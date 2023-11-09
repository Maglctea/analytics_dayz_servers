from dataclasses import dataclass


@dataclass
class Server:
    id: int
    name: str
    top: int
    status: str
    ip: str
    version: str
    map: str
    uptime: str
    added_at: str
    checked_at: str
    online_at: str
