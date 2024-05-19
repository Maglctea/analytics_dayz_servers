from typing import Protocol


class IAuthGateway(Protocol):
    def hash_secret(self, secret: str):
        raise NotImplementedError

    def generate_jwt_token(
            self,
            user_id: int,
            algorithm: str,
            secret_key: str,
            expires_delta_minutes: int
    ):
        raise NotImplementedError
