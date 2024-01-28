import logging

from dayz.application.models.user import UserData
from dayz.database.core import create_session_maker, new_session
from dayz.database.orm.user import UserGateway

logger = logging.getLogger(__name__)


def get_user(
        username: str,
        password: str
) -> UserData | None:
    engine = create_session_maker()
    session = new_session(engine)
    gate = UserGateway(session=next(session))
    user = gate.get_user(
        username=username,
        password=password
    )
    return user
