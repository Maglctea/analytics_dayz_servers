from pydantic_settings import BaseSettings


class StorageConfig(BaseSettings):
    media_folder: str = '/app/media'

    class Config:
        env_prefix = 'STORAGE_'
