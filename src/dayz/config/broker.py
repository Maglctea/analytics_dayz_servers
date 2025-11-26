from pydantic_settings import BaseSettings


class BrokerConfig(BaseSettings):
    user: str = 'admin'
    password: str
    host: str = 'amqp://admin:dayzadmin_4632@rabbitmq:5672/'

    class Config:
        env_prefix = 'BROKER_'
