from sqlalchemy.orm import Mapped

from src.models.base import BaseModel


class UserModel(BaseModel):
    __tablename__ = 'users'

    username: Mapped[str]
    password: Mapped[str]
