import asyncio
import logging
import os

import uvicorn
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import I18nConfig
from starlette_admin.contrib.sqla import Admin
from starlette_admin.views import Link

from dayz.domain.dto.configs.api import APIConfig
from dayz.domain.dto.configs.auth import AuthConfig
from dayz.domain.dto.configs.db import DBConfig
from dayz.infrastructure.config_loader import load_config
from dayz.infrastructure.db.models.server import PVPServer, PVEServer
from dayz.infrastructure.di.config import AuthConfigProvider, AdminConfigProvider
from dayz.infrastructure.di.db import DbProvider
from dayz.infrastructure.di.gateway import GatewaysProvider
from dayz.infrastructure.di.interactor import AdminInteractorProvider
from dayz.presentation.admin.auth import AdminAuthProvider
from dayz.presentation.admin.views.pve_servers import PVEServerAdminView
from dayz.presentation.admin.views.pvp_servers import PVPServerAdminView

logger = logging.getLogger(__name__)


def setup_admin_views(admin: Admin) -> None:
    pass
    admin.add_view(Link(label="API Docs", url="/docs", icon="fa-solid fa-code"))

    # Servers
    admin.add_view(
        PVPServerAdminView(
            label='PVP Сервера',
            identity='pvp_server',
            model=PVPServer,
            icon="fa-solid fa-server",
        ),
    )

    admin.add_view(
        PVEServerAdminView(
            label='PVE Сервера',
            identity='pve_server',
            model=PVEServer,
            icon="fa-solid fa-server",
        ),
    )


async def setup_admin_app(
        app: FastAPI,
        container: AsyncContainer
) -> None:
    basedir = os.path.abspath(os.path.dirname(__file__))
    templates_dir = os.path.join(basedir, "templates")

    admin = Admin(
        engine=await container.get(AsyncEngine),
        title='Manager deals admin',
        templates_dir=templates_dir,
        i18n_config=I18nConfig(default_locale="ru"),
        auth_provider=AdminAuthProvider(container=container),
        debug=True,
        base_url='',
    )
    admin.mount_to(app)
    setup_admin_views(admin)


def init_api(
        api_config: APIConfig,
        auth_config: AuthConfig
) -> FastAPI:
    logger.debug("Initialize API")
    app = FastAPI(
        debug=api_config.debug,
        title="User service",
        version="1.0.0"
    )
    app.add_middleware(SessionMiddleware, secret_key=auth_config.secret_key)
    return app


async def run_api(
        app: FastAPI,
        api_config: APIConfig
) -> None:
    config = uvicorn.Config(
        app,
        host=api_config.host,
        port=api_config.port,
        reload=api_config.debug,
    )
    server = uvicorn.Server(config)
    logger.info("Running API")
    await server.serve()


async def main() -> None:
    api_config = load_config(
        config_type=APIConfig,
        config_scope='api',
    )

    auth_config = load_config(
        config_type=AuthConfig,
        config_scope='auth',
    )

    db_config = load_config(
        config_type=DBConfig,
        config_scope='db',
    )

    logger.info("Initializing DI")

    container = make_async_container(
        AuthConfigProvider(),
        AdminConfigProvider(),
        DbProvider(config=db_config),
        GatewaysProvider(),
        AdminInteractorProvider(),

    )

    logger.info("Initializing admin")
    app = init_api(
        api_config=api_config,
        auth_config=auth_config
    )
    await setup_admin_app(
        app=app,
        container=container
    )

    if api_config.debug:
        logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)

    setup_dishka(container, app)
    await run_api(app, api_config)


if __name__ == '__main__':
    asyncio.run(main())
