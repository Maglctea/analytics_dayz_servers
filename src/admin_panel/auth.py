import hashlib

from fastapi.requests import Request
from sqladmin.authentication import AuthenticationBackend

from src import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get('username', '')
        password = form.get('password', '').encode('utf8')
        hashpass = hashlib.sha256(password)


        # engine = create_session_maker()
        # session = new_session(engine)
        # gate = UserGateway(next(session))
        #
        # user = gate.get_user(
        #     username=username,
        #     password=hashpass.hexdigest()
        # )
        #
        # if user is None:
        #     return False

        request.session.update({"auth_status": "success"})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        status = request.session.get("auth_status")
        if not status or status != "success":
            return False

        return True


authentication_backend = AdminAuth(secret_key=settings.ADMIN_PANEL_SECRET_KEY)
