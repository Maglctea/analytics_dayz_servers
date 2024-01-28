from sqlalchemy.orm import Mapped

from dayz.application.models.user import UserData
from dayz.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str]
    password: Mapped[str]

    def to_dataclass(self) -> UserData:
        return UserData(
            id=self.id,
            username=self.username,
            password=self.password
        )

    @staticmethod
    def to_model(user: UserData) -> 'UserModel':
        return UserModel(
            username=user.username,
            password=user.password
        )
