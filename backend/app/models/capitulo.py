from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Capitulo(Base):
    """Versão mínima, só o que a Jornada precisa. A issue de Quadrinhos (#10)
    completa este model (páginas com imagem, texto...)."""

    __tablename__ = "capitulos"
    # cada opção de uma decisão leva a no máximo um capítulo
    __table_args__ = (UniqueConstraint("pai_id", "opcao_origem"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    historia_id: Mapped[int] = mapped_column(ForeignKey("historias.id"), index=True)
    numero: Mapped[int]
    titulo: Mapped[str] = mapped_column(String(200))
    # Jornada: capítulo anterior e a opção vencedora que levou até este (None na raiz)
    pai_id: Mapped[int | None] = mapped_column(ForeignKey("capitulos.id"), default=None)
    opcao_origem: Mapped[int | None] = mapped_column(default=None)
    texto: Mapped[str] = mapped_column(String(4000), default="")
    imagem_url: Mapped[str | None] = mapped_column(String(300), default=None)
