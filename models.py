from sqlalchemy import Table, Text, Integer, String, MetaData, Column

metadata_obj = MetaData()

server_table = Table(
    'server',
    metadata_obj,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, unique=True),
    Column('address', String, unique=True),
    Column('port', Integer),
    Column('query_port', Integer),
    Column('mode', String),
    Column('registration_type', String),
    Column('description', Text),
    Column('invite_code', String),
    Column('banner_url', String),
    Column('message_id', Integer)

)
