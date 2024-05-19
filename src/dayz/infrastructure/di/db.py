from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from dayz.application.interfaces.uow import IUoW
from dayz.domain.dto.configs.db import DBConfig
from dayz.infrastructure.db.core import create_engine, create_session_factory
from dayz.infrastructure.db.uow import UoW


class DbProvider(Provider):
    def __init__(self, config: DBConfig):
        super().__init__()
        self.config = config

    scope = Scope.APP

    @provide
    async def get_engine(self) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(
            full_url=self.config.full_url,
            echo=self.config.echo
        )
        yield engine
        await engine.dispose(True)

    @provide
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    uow = provide(
        source=UoW,
        provides=IUoW,
        scope=Scope.REQUEST
    )
