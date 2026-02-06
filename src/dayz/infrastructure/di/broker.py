from typing import AsyncIterable

from dishka import Provider, Scope, provide
from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext

from dayz.config import BrokerConfig


class BrokerProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self, broker_config: BrokerConfig) -> AsyncIterable[RabbitBroker]:
        async with RabbitBroker(
                host=broker_config.host,
                security=SASLPlaintext(
                    username=broker_config.user,
                    password=broker_config.password,
                )
        ) as broker:
            yield broker
