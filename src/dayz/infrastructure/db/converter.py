from adaptix._internal.conversion.facade.func import get_converter

from dayz.domain.dto.server import ServerDTO
from dayz.infrastructure.db.models import PVPServer

convert_server_to_dto = get_converter(PVPServer, ServerDTO)
convert_dto_to_server = get_converter(ServerDTO, PVPServer)

model_to_server_converter = get_converter(
    PVPServer,
    ServerDTO
)
