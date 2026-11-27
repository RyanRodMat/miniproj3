from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


class Historia(Base):
    """História interativa: o artista publica capítulos e a rede vota o rumo."""

    __tablename__ = "historias"

    id: Mapped[int] = mapped_column(primary_key=True)
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    titulo: Mapped[str] = mapped_column(String(120))
    sinopse: Mapped[str] = mapped_column(String(500), default="")
    tag: Mapped[str] = mapped_column(String(30), index=True)  # tag principal (= tags[0])
    # todas as tags separadas por vírgula (vazio = só `tag`); ver services/historias.py
    tags: Mapped[str] = mapped_column(String(200), default="")
    capa_url: Mapped[str | None] = mapped_column(String(300), default=None)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    autor: Mapped[User] = relationship(lazy="joined")


class Capitulo(Base):
    __tablename__ = "capitulos"

    id: Mapped[int] = mapped_column(primary_key=True)
    historia_id: Mapped[int] = mapped_column(ForeignKey("historias.id"), index=True)
    ordem: Mapped[int]
    titulo: Mapped[str] = mapped_column(String(120))
    texto: Mapped[str] = mapped_column(String(4000), default="")
    # capítulos do seed têm 1 imagem aqui; os novos usam `Pagina` (imagem_url = 1ª página)
    imagem_url: Mapped[str | None] = mapped_column(String(300), default=None)


class Pagina(Base):
    """Uma página (imagem) do capítulo; o leitor mostra por `ordem`, de cima para baixo."""

    __tablename__ = "paginas"

    id: Mapped[int] = mapped_column(primary_key=True)
    capitulo_id: Mapped[int] = mapped_column(ForeignKey("capitulos.id"), index=True)
    ordem: Mapped[int]
    imagem_url: Mapped[str] = mapped_column(String(300))
