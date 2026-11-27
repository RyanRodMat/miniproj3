from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Comentario(Base):
    __tablename__ = "comentarios"
    # exatamente um alvo: ou post, ou capítulo
    __table_args__ = (
        CheckConstraint(
            "(post_id IS NULL) != (capitulo_id IS NULL)", name="ck_comentario_um_alvo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int | None] = mapped_column(
        ForeignKey("posts.id"), index=True, default=None
    )
    capitulo_id: Mapped[int | None] = mapped_column(
        ForeignKey("capitulos.id"), index=True, default=None
    )
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    texto: Mapped[str] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    autor = relationship("User", lazy="joined")