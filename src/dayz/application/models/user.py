from dataclasses import dataclass


@dataclass
class UserData:
    username: str
    password: str
    id: int | None = None
