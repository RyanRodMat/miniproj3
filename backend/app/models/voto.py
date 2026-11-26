from datetime import datetime, timezone

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Voto(Base):
    """Um voto por usuário por decisão (chave composta)."""

    __tablename__ = "votos"

    decisao_id: Mapped[int] = mapped_column(ForeignKey("decisoes.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    opcao: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
