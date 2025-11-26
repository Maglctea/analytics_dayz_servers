from pydantic_settings import BaseSettings


class APIConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8100
    debug: bool = False

    class Config:
        env_prefix = 'API_'
