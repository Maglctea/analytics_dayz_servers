from typing import Protocol

from dayz.domain.dto.user import UserData


class IUserGateway(Protocol):
    async def get_user_by_id(self, user_id: int) -> UserData | None:
        raise NotImplementedError

    async def get_user_by_login(self, login: str) -> UserData | None:
        raise NotImplementedError
