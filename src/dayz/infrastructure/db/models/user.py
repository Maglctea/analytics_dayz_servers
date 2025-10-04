from sqlalchemy.orm import Mapped, mapped_column

from dayz.domain.dto.user import UserData
from dayz.infrastructure.db.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False
    )
    username: Mapped[str]
    hashed_password: Mapped[str]

    def to_dataclass(self) -> UserData:
        return UserData(
            id=self.id,
            username=self.username,
            hashed_password=self.hashed_password
        )

    @staticmethod
    def to_model(user: UserData) -> 'UserModel':
        return UserModel(
            username=user.username,
            hashed_password=user.hashed_password
        )
