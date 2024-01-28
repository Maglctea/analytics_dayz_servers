from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models.user import UserModel


class UserGateway:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(
            self,
            username: str,
            password: str
    ):
        stmt = select(UserModel).filter(UserModel.username == username, UserModel.password == password)
        user = self.session.scalar(stmt)
        return user

# engine = create_session_maker()
# session = new_session(engine)
# gate = UserGateway(session=next(session))
#
# user = gate.get_user('admin', 'admindayz_4632')
# pass