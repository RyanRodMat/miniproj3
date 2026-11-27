from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


class Historia(Base):
    """História em capítulos; a Jornada (votação) usa os capítulos encadeados."""

    __tablename__ = "historias"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    sinopse: Mapped[str] = mapped_column(String(500), default="")
    tag: Mapped[str] = mapped_column(String(30), default="", index=True)  # principal (= tags[0])
    # todas as tags separadas por vírgula (vazio = só `tag`); ver services/historias.py
    tags: Mapped[str] = mapped_column(String(200), default="")
    capa_url: Mapped[str | None] = mapped_column(String(300), default=None)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    autor: Mapped[User] = relationship(lazy="joined")
