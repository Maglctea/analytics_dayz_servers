from pydantic_settings import BaseSettings


class AdminConfig(BaseSettings):
    host: str = '0.0.0.0'
    port: int = 8200
    debug: bool = False
    secret_key: str

    class Config:
        env_prefix = 'ADMIN_'
