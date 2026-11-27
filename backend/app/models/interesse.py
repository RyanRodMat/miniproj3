from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Interesse(Base):
    """Tag de interesse de um usuário (ex.: "fantasia"). Chave composta: sem repetir."""

    __tablename__ = "interesses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    tag: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
