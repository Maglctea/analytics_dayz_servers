import sqlite3
from datetime import datetime
from sqlite3 import Connection, Cursor
import logging
import traceback

logger = logging.getLogger(__name__)


def initialize_db(connection: Connection, cursor: Cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS server(server_id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255), address VARCHAR(255), port INT, query_port INT)')
    connection.commit()


def add_server(
        connection: Connection,
        cursor: Cursor,
        name: str,
        address: str,
        port: int,
        query_port: int
) -> tuple[bool, int | Exception]:
    try:
        cursor.execute('INSERT INTO server (name, address, port, query_port) VALUES (?, ?, ?, ?)',
                       (name, address, port, query_port))
        server_id = cursor.lastrowid
        connection.commit()
        return True, server_id
    except Exception as e:
        logger.exception(f'{datetime.now()}: Error: {traceback.format_exc()}')
        return False, e


def get_servers(cursor: Cursor) -> list[str, int]:
    res = cursor.execute('SELECT * FROM server')
    servers = res.fetchall()
    return servers


def get_server(cursor: Cursor, server_id: int = None, address: str = None):
    if server_id is not None:
        res = cursor.execute('SELECT * FROM server WHERE server_id = ?', (address,))
    else:
        res = cursor.execute('SELECT * FROM server WHERE address = ?', (address,))
    server = res.fetchone()
    if server is None:
        pass
    return server


def delite_servers(connection: Connection, cursor: Cursor, server_id: int) -> bool:
    try:
        cursor.execute('DELETE FROM server WHERE server_id = ?', (server_id,))
        connection.commit()
        return True
    except Exception as e:
        logger.exception(f'{datetime.now()}: Error: {traceback.format_exc()}')
        return False
