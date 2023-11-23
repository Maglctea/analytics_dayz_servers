from sqlalchemy import insert, select, update, delete

from database.core import sync_engine
from models import server_table
from schemes import ServerInfo


def add_server(server: ServerInfo):
    with sync_engine.connect() as connection:
        stmt = insert(server_table).values(server.__dict__)
        result = connection.execute(stmt)
        connection.commit()
    return result.inserted_primary_key[0]


def update_server(server: ServerInfo):
    with sync_engine.connect() as connection:
        stmt = update(server_table).where(server_table.c.name == server.name).values(server.__dict__)
        connection.execute(stmt)
        connection.commit()
    return True


def get_server(message_id: int):
    with sync_engine.connect() as connection:
        stmt = select(server_table).where(server_table.c.message_id == message_id)
        result = connection.execute(stmt).first()

        if result is None:
            return None

        id_server, name, address, port, query_port, mode, registration_type, description, invite_code, banner_url, message_id = result
        return ServerInfo(
            name=name,
            address=address,
            port=port,
            query_port=query_port,
            mode=mode,
            registration_type=registration_type,
            description=description,
            invite_code=invite_code,
            banner_url=banner_url,
            message_id=message_id
        )


def get_servers() -> list[ServerInfo] | None:
    with sync_engine.connect() as connection:
        stmt = select(server_table)
        servers = connection.execute(stmt).fetchall()

        if servers is None:
            return None
        servers_info_list = []
        for server in servers:
            id_server, name, address, port, query_port, mode, registration_type, description, invite_code, banner_url, message_id = server
            server_info = ServerInfo(
                name=name,
                address=address,
                query_port=query_port,
                port=port,
                mode=mode,
                registration_type=registration_type,
                description=description,
                invite_code=invite_code,
                banner_url=banner_url,
                message_id=message_id
            )
            servers_info_list.append(server_info)
    return servers_info_list


def delete_server(message_id: str):
    with sync_engine.connect() as connection:
        stmt = delete(server_table).where(server_table.c.message_id == message_id)
        connection.execute(stmt)
        connection.commit()
    return True
