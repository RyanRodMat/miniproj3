from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    bio: Mapped[str] = mapped_column(String(280), default="")
    avatar_url: Mapped[str] = mapped_column(String(300), default="")
    password_hash: Mapped[str] = mapped_column(String(100), default="")
    tipo: Mapped[str] = mapped_column(String(10), default="leitor")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    interesses: Mapped[list["Interesse"]] = relationship(  # noqa: F821
        lazy="selectin", cascade="all, delete-orphan", order_by="Interesse.tag"
    )

    @property
    def tags_interesse(self) -> list[str]:
        return [i.tag for i in self.interesses]
