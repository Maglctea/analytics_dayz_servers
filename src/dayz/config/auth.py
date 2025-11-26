from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    secret_key: str
    token_expire_minutes: int = 60
    algorithm: str = "HS256"

    class Config:
        env_prefix = 'AUTH_'
