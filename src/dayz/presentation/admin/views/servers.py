import os

from faststream.rabbit import RabbitBroker
from starlette.requests import Request
from starlette_admin import fields
from starlette_admin.contrib.sqla import ModelView

from dayz.infrastructure.db.converter import model_to_server_converter
from dayz.infrastructure.db.models.server import Server


class ServerAdminView(ModelView):
    name = "Server"
    identity = 'server'
    label = 'Аккаунт'

    fields = [
        Server.id,
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
        Server.address,
        Server.port,
        Server.query_port,
        Server.mode,
        Server.registration_type,
        Server.description,
        Server.invite_code,
        Server.banner_url,
        Server.message_id,
        Server.forum_id
    ]

    sortable_fields = [
        Server.id,
        Server.name,
        Server.registration_type,
    ]

    exclude_fields_from_create = [
        Server.message_id,
        Server.forum_id
    ]

    searchable_fields = [
        Server.id,
        Server.name,
        Server.address,
        Server.registration_type,
    ]
    page_size = 50

    async def can_edit(self, request: Request) -> bool:
        return False

    async def after_create(self, request: Request, obj: Server) -> None:
        async with RabbitBroker(os.getenv('RABBITMQ_HOST')) as broker:
            await broker.publish(
                model_to_server_converter(obj),
                queue='add_server'
            )

    async def after_delete(self, request: Request, obj: Server) -> None:
        async with RabbitBroker(os.getenv('RABBITMQ_HOST')) as broker:
            await broker.publish(
                model_to_server_converter(obj),
                queue='delete_server'
            )
