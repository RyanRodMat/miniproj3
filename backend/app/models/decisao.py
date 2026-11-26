from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Decisao(Base):
    """Bifurcação no fim de um capítulo. `aberta` = a votação ainda está rolando."""

    __tablename__ = "decisoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    capitulo_id: Mapped[int] = mapped_column(ForeignKey("capitulos.id"), index=True)
    pergunta: Mapped[str] = mapped_column(String(200))
    aberta: Mapped[bool] = mapped_column(default=True)


class Opcao(Base):
    __tablename__ = "opcoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    decisao_id: Mapped[int] = mapped_column(ForeignKey("decisoes.id"), index=True)
    texto: Mapped[str] = mapped_column(String(200))


class Voto(Base):
    """Um voto por usuário por decisão (chave composta)."""

    __tablename__ = "votos"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    decisao_id: Mapped[int] = mapped_column(
        ForeignKey("decisoes.id"), primary_key=True
    )
    opcao_id: Mapped[int] = mapped_column(ForeignKey("opcoes.id"), index=True)
