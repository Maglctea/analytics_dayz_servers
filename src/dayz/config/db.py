from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    host: str = 'db'
    port: int = 5432
    database: str = 'dayz'
    user: str = 'postgres'
    password: str = 'password'
    echo: bool = False
    driver: str = 'asyncpg'
    db_type: str = 'postgresql'

    @property
    def full_url(self) -> str:
        return f"{self.db_type}+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    class Config:
        env_prefix = 'DB_'
