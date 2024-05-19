from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dayz.application.interfaces.user import IUserGateway
from dayz.domain.dto.user import UserData
from dayz.infrastructure.db.models.user import UserModel


class UserGateway(IUserGateway):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_id(self, user_id: int) -> UserData | None:
        user = await self.session.get(UserModel, user_id)

        if user is None:
            return None

        user_data = UserData(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password
        )
        return user_data

    async def get_user_by_login(self, login: str) -> UserData | None:
        user = await self.session.scalar(
            select(UserModel)
            .where(UserModel.username == login)
        )

        if user is None:
            return None

        user_data = UserData(
            id=user.id,
            username=user.username,
            hashed_password=user.hashed_password
        )
        return user_data
