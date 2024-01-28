import hashlib

from fastapi.requests import Request
from sqladmin.authentication import AuthenticationBackend

from dayz import settings
from dayz.admin_panel.service import get_user


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get('username', '')
        password = form.get('password', '').encode('utf8')
        hashpass = hashlib.sha256(password)

        user = get_user(
            username=username,
            password=hashpass.hexdigest()
        )

        if user is None:
            return False

        request.session.update({"auth_status": "success"})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        status = request.session.get("auth_status")
        return status or status == "success"



authentication_backend = AdminAuth(secret_key=settings.ADMIN_PANEL_SECRET_KEY)
