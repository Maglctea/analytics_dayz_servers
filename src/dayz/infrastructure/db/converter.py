from adaptix._internal.conversion.facade.func import get_converter
from adaptix._internal.conversion.facade.provider import allow_unlinked_optional

from dayz.application.scheme.server import CreateServerScheme
from dayz.domain.dto.server import ServerDTO, CreateServerDTO, CreateServerDTO
from dayz.infrastructure.db.models import PVPServer

convert_server_to_dto = get_converter(PVPServer, ServerDTO)
convert_dto_to_server = get_converter(ServerDTO, PVPServer)

# convert_create_dto_to_server = get_converter(
#     CreateServerDTO,
#     Server,
#     recipe=[allow_unlinked_optional('id')]
# )
#
# convert_create_server_to_dto = get_converter(
#     CreateServerScheme,
#     CreateServerDTO
# )


#
# server = CreateServerScheme(
#     name='test',
#     address='127.0.0.1',
#     port=213,
#     query_port=5432,
#     mode='test mode',
#     registration_type='my_type',
#     description='test description',
#     invite_code='dfsdfcsdf',
#     banner_url='https/test.ru',
#     message_id=123213
# )
# dto = convert_create_server_to_dto(server)
# server = convert_create_dto_to_server(dto)

# server_model = Server(
#     id=1,
#     name='test',
#     address='127.0.0.1',
#     port=213,
#     query_port=5432,
#     mode='test mode',
#     registration_type='my_type',
#     description='test description',
#     invite_code='dfsdfcsdf',
#     banner_url='https/test.ru',
#     message_id=1234,
#     forum_id=12323
# )
model_to_server_converter = get_converter(
    PVPServer,
    ServerDTO
)

# model_to_server_converter = get_converter(
#     Server,
#     ServerDTO
# )

# retort = Retort()
# retort.load(server, CreateServerDTO)
