from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Historia(Base):
    """Versão mínima, só o que a Jornada precisa. A issue de Quadrinhos (#10)
    completa este model (sinopse, capa, tags...)."""

    __tablename__ = "historias"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    autor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
