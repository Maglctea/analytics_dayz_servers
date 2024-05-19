from pydantic import BaseModel


class CreateServerScheme(BaseModel):
    name: str
    address: str
    port: int
    query_port: int
    mode: str
    registration_type: str
    description: str
    invite_code: str
    banner_url: str
    message_id: int


class ServerScheme(CreateServerScheme):
    id: int


class AddServerResponse(BaseModel):
    message_id: int
    server_id: int
