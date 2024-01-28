from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(MappedAsDataclass, DeclarativeBase):
    id: Mapped[int] = mapped_column(
        init=False,
        primary_key=True,
        autoincrement=True,
        index=True,
        nullable=False
    )
