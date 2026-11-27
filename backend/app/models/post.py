from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.user import User


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    texto: Mapped[str] = mapped_column(String(2000))
    # None = post só de texto; preenchido = post de arte (o upload é outra issue)
    imagem_url: Mapped[str | None] = mapped_column(String(300), default=None)
    # preenchido nos posts automáticos de "novo capítulo" (o card linka a história)
    historia_id: Mapped[int | None] = mapped_column(
        ForeignKey("historias.id"), default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )

    autor: Mapped[User] = relationship(lazy="joined")
