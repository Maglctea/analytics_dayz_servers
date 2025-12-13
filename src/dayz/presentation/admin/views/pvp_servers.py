import os

from faststream.rabbit import RabbitBroker
from starlette.requests import Request
from starlette_admin import fields
from starlette_admin.contrib.sqla import ModelView

from dayz.config import BrokerConfig
from dayz.infrastructure.db.converter import model_to_server_converter
from dayz.infrastructure.db.models.server import PVPServer


class PVPServerAdminView(ModelView):
    name = "PVP Server"
    identity = 'pvp_server'
    label = 'Аккаунт'

    fields = [
        PVPServer.id,
        # Server.name,
        fields.StringField('name', 'Название', required=True),
        fields.StringField('address', 'IP адрес', required=True),
        fields.IntegerField('port', 'Порт', required=True),
        fields.IntegerField('query_port', 'Query порт', required=True),
        fields.StringField('mode', 'Режим игры', required=True),
        fields.StringField('registration_type', 'Вид регистрации', required=True),
        fields.TextAreaField('description', 'Описание', required=True, maxlength=1500),
        fields.StringField('invite_code', 'Инвайт код сервера (только код, без ссылки)', required=True),
        fields.StringField('banner_url', 'Ссылка на картинку сервера', required=True),
        fields.IntegerField('message_id', 'ID сообщения', required=True),
        fields.IntegerField('forum_id', 'ID форума', required=True),
    ]

    exclude_fields_from_list = [
        PVPServer.address,
        PVPServer.port,
        PVPServer.query_port,
        PVPServer.mode,
        PVPServer.registration_type,
        PVPServer.description,
        PVPServer.invite_code,
        PVPServer.banner_url,
        PVPServer.message_id,
        PVPServer.forum_id
    ]

    sortable_fields = [
        PVPServer.id,
        PVPServer.name,
        PVPServer.registration_type,
    ]

    exclude_fields_from_create = [
        PVPServer.message_id,
        PVPServer.forum_id
    ]

    searchable_fields = [
        PVPServer.id,
        PVPServer.name,
        PVPServer.address,
        PVPServer.registration_type,
    ]
    page_size = 50

    broker_config: BrokerConfig = BrokerConfig()

    async def can_edit(self, request: Request) -> bool:
        return False

    async def after_create(self, request: Request, obj: PVPServer) -> None:
        async with RabbitBroker(self.broker_config.url) as broker:
            await broker.publish(
                model_to_server_converter(obj),
                queue='add_pvp_server'
            )

    async def after_delete(self, request: Request, obj: PVPServer) -> None:
        async with RabbitBroker(self.broker_config.url) as broker:
            await broker.publish(
                model_to_server_converter(obj),
                queue='delete_pvp_server'
            )
