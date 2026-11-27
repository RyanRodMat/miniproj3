from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Pagina(Base):
    """Uma página (imagem) do capítulo; o leitor mostra por `ordem`, de cima para baixo."""

    __tablename__ = "paginas"

    id: Mapped[int] = mapped_column(primary_key=True)
    capitulo_id: Mapped[int] = mapped_column(ForeignKey("capitulos.id"), index=True)
    ordem: Mapped[int]
    imagem_url: Mapped[str] = mapped_column(String(300))
