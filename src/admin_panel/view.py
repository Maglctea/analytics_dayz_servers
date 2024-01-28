from sqladmin import ModelView
from src.models.server import ServerModel


class ServerAdmin(ModelView, model=ServerModel):
    column_list = [ServerModel.id, ServerModel.name]
    name_plural = 'Servers'
    name = 'Server'

