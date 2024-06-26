from dayz.application.interfaces.uow import IUoW
from dayz.application.interfaces.user import IUserGateway
from dayz.domain.dto.configs.auth import AuthConfig
from dayz.domain.exceptions.user import UserNotFoundException
from dayz.infrastructure.auth.security import hash_secret, generate_jwt_token


class BaseLoginInteractor:
    def __init__(
            self,
            user_gateway: IUserGateway,
            auth_config: AuthConfig
    ) -> None:
        self.user_gateway = user_gateway
        self.auth_config = auth_config

    async def __call__(
            self,
            login: str,
            password: str
    ) -> str:
        user = await self.user_gateway.get_user_by_login(login)

        if user is not None:
            if user.hashed_password == hash_secret(password):
                token = generate_jwt_token(

                    user_id=user.id,
                    expires_delta_minutes=self.auth_config.token_expire_minutes,
                    algorithm=self.auth_config.algorithm,
                    secret_key=self.auth_config.secret_key
                )
                return token

        raise UserNotFoundException('The user with such private data was not found')
