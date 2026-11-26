from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Historia(Base):
    """História interativa: o artista publica capítulos e a rede vota o rumo."""

    __tablename__ = "historias"

    id: Mapped[int] = mapped_column(primary_key=True)
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    titulo: Mapped[str] = mapped_column(String(120))
    sinopse: Mapped[str] = mapped_column(String(500), default="")
    tag: Mapped[str] = mapped_column(String(30), index=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )


class Capitulo(Base):
    __tablename__ = "capitulos"

    id: Mapped[int] = mapped_column(primary_key=True)
    historia_id: Mapped[int] = mapped_column(ForeignKey("historias.id"), index=True)
    ordem: Mapped[int]
    titulo: Mapped[str] = mapped_column(String(120))
    texto: Mapped[str] = mapped_column(String(4000))
    imagem_url: Mapped[str | None] = mapped_column(String(300), default=None)
