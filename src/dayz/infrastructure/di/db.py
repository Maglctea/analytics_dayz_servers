from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, AsyncEngine

from dayz.application.interfaces.uow import IUoW
from dayz.config import DBConfig
from dayz.infrastructure.db.core import create_engine, create_session_factory
from dayz.infrastructure.db.uow import UoW


class DbProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_engine(self, db_config: DBConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(
            full_url=db_config.full_url,
            echo=db_config.echo
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
