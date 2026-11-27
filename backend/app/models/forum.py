from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


class Forum(Base):
    __tablename__ = "foruns"

    id: Mapped[int] = mapped_column(primary_key=True)
    # nome único sem diferenciar maiúsculas (a checagem é no service; o índice pega a corrida)
    nome: Mapped[str] = mapped_column(String(60), unique=True)
    descricao: Mapped[str] = mapped_column(String(300), default="")
    criador_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )


class ForumMembro(Base):
    """Quem participa do fórum. Chave composta: entrar duas vezes não duplica."""

    __tablename__ = "forum_membros"

    forum_id: Mapped[int] = mapped_column(ForeignKey("foruns.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )


class ForumPost(Base):
    """Post de fórum: tabela própria, por isso nunca entra no feed pessoal."""

    __tablename__ = "forum_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    forum_id: Mapped[int] = mapped_column(ForeignKey("foruns.id"), index=True)
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    texto: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )

    autor: Mapped[User] = relationship(lazy="joined")
