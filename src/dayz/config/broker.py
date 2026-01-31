from pydantic_settings import BaseSettings


class BrokerConfig(BaseSettings):
    user: str = 'admin'
    password: str
    host: str = 'rabbitmq'
    port: int = 5672

    class Config:
        env_prefix = 'BROKER_'

    @property
    def url(self) -> str:
        return f'amqp://{self.user}:{self.password}@{self.host}:{self.port}/'