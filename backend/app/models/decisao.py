from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Decisao(Base):
    """O capítulo termina numa decisão: 2 a 4 opções, votação até o prazo."""

    __tablename__ = "decisoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    capitulo_id: Mapped[int] = mapped_column(ForeignKey("capitulos.id"), unique=True)
    pergunta: Mapped[str] = mapped_column(String(300))
    opcoes: Mapped[list[str]] = mapped_column(JSON)
    # UTC sem fuso (o SQLite não guarda tzinfo); o schema devolve com "Z"
    prazo: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
