from dishka import AsyncContainer
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AuthProvider, AdminConfig, AdminUser
from starlette_admin.exceptions import LoginFailed

from dayz.application.account.auth import BaseLoginInteractor
from dayz.domain.exceptions.user import AccessDeniedException, UserNotFoundException
from dayz.infrastructure.auth.access import JWTGetUserService


class AdminAuthProvider(AuthProvider):
    def __init__(
            self,
            container: AsyncContainer
    ):
        super().__init__()
        self.container = container

    """
    This is only for demo purpose, it's not a better
    way to save and validate user credentials
    """

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response,
    ) -> Response:
        async with self.container() as request_container:
            login_interactor = await request_container.get(BaseLoginInteractor)
            try:
                access_token = await login_interactor(username, password)
                request.session.update({"token": access_token})
            except UserNotFoundException:
                raise LoginFailed("Неверный логин или пароль")
            return response

    async def is_authenticated(self, request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        async with self.container() as request_container:
            get_user_service = await request_container.get(JWTGetUserService)

            try:
                user = await get_user_service(token=token)
                if user:
                    request.state.user = user
                    return True
            except AccessDeniedException:
                return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        return AdminConfig(
            app_title='Dayz RP',
            logo_url='https://sun9-58.userapi.com/impg/xzVhimYaCwHRA9_Iz-es7Quu3bvXQIlKJCjDiQ/_9zUVymXWpI.jpg?size=1024x1024&quality=95&sign=aaa126473fbccd384354594cc8e290d2&type=album',
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user.username  # Retrieve current user
        return AdminUser(
            username=user
        )

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
