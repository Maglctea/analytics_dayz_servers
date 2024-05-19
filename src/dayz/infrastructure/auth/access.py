from jose import JWTError

from dayz.application.interfaces.user import IUserGateway
from dayz.domain.dto.configs.auth import AuthConfig
from dayz.domain.dto.user import UserData
from dayz.domain.exceptions.user import AccessDeniedException
from dayz.infrastructure.auth.security import parse_jwt_token


class JWTGetUserService:
    def __init__(
            self,
            user_gateway: IUserGateway,
            auth_config: AuthConfig
    ) -> None:
        self.user_gateway = user_gateway
        self.auth_config = auth_config

    async def __call__(
            self,
            token: str,
    ) -> UserData:

        try:
            token_data = parse_jwt_token(
                token=token,
                secret_key=self.auth_config.secret_key,
                algorithm=self.auth_config.algorithm
            )
        except JWTError:
            raise AccessDeniedException('Invalid or expired token')

        user = await self.user_gateway.get_user_by_id(token_data.get('user_id'))
        return user
