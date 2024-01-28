from sqlalchemy import select
from sqlalchemy.orm import Session

from dayz.application.models.user import UserData
from dayz.database.core import create_session_maker, new_session
from dayz.models.user import UserModel


class UserGateway:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(
            self,
            username: str,
            password: str
    ) -> UserData | None:
        stmt = select(UserModel).filter(UserModel.username == username, UserModel.password == password)
        user = self.session.scalar(stmt)

        if user:
            return user.to_dataclass()
        return None
