import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqladmin import Admin

from dayz.admin_panel.auth import authentication_backend
from dayz.admin_panel.view import ServerAdmin
from dayz.database.core import get_engine

app = FastAPI()

admin = Admin(
    app=app,
    engine=get_engine(),
    authentication_backend=authentication_backend
)

admin.add_view(ServerAdmin)


@app.get('/')
async def admin_panel():
    return RedirectResponse('admin/')


