from sqlalchemy import create_engine
from models import metadata_obj

sync_engine = create_engine(
    url='sqlite:///dayz.db',
    echo=False,
)


def create_tables():
    # metadata_obj.drop_all(sync_engine)
    metadata_obj.create_all(sync_engine)
