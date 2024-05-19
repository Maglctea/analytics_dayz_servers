from dataclasses import dataclass


@dataclass
class UserData:
    username: str
    hashed_password: str
    id: int | None = None
