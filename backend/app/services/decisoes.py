from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.em_alta import em_alta
from app.core.jornada import jornada
from app.models.capitulo import Capitulo
from app.models.decisao import Decisao
from app.models.historia import Historia
from app.models.pagina import Pagina
from app.models.post import Post
from app.models.user import User
from app.models.voto import Voto
from app.schemas.jornada import (
    CapituloCreate,
    DecisaoCreate,
    DecisaoJornadaOut,
    DecisaoOut,
    JornadaOut,
    OpcaoJornadaOut,
    OpcaoOut,
    PassoOut,
)
from app.services import em_alta as service_em_alta
from app.services import tags


def _agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _com_fuso(dt: datetime) -> datetime:
    return dt.replace(tzinfo=timezone.utc)


def _votos_por_opcao(db: Session, decisao: Decisao) -> list[int]:
    linhas = dict(
        db.execute(
            select(Voto.opcao, func.count())
            .where(Voto.decisao_id == decisao.id)
            .group_by(Voto.opcao)
        ).all()
    )
    return [linhas.get(i, 0) for i in range(len(decisao.opcoes))]


def _decisao(db: Session, decisao_id: int) -> Decisao:
    decisao = db.get(Decisao, decisao_id)
    if not decisao:
        raise HTTPException(status_code=404, detail="decisão não encontrada")
    return decisao


def sincronizar(db: Session, decisao: Decisao) -> None:
    """Votação com prazo vencido: avisa a árvore (fecha o nó). Idempotente.

    O encerramento é detectado na primeira leitura/escrita depois do prazo, em vez de
    um timer: não há processo em segundo plano e o resultado é o mesmo."""
    if decisao.prazo <= _agora() and not jornada.encerrada(decisao.capitulo_id):
        jornada.encerrar(decisao.capitulo_id, _votos_por_opcao(db, decisao))


def reconstruir_jornada(db: Session) -> None:
    """Startup: refaz a árvore a partir do banco. O(n)."""
    capitulos = [
        (c.id, c.historia_id, c.pai_id, c.opcao_origem)
        for c in db.scalars(select(Capitulo).order_by(Capitulo.id))
    ]
    agora = _agora()
    decisoes = []
    for d in db.scalars(select(Decisao)):
        votos = _votos_por_opcao(db, d) if d.prazo <= agora else None
        decisoes.append((d.capitulo_id, d.opcoes, votos))
    jornada.reconstruir(capitulos, decisoes)


def _out(db: Session, user: User, decisao: Decisao) -> DecisaoOut:
    sincronizar(db, decisao)
    votos = _votos_por_opcao(db, decisao)
    meu = db.get(Voto, (decisao.id, user.id))
    return DecisaoOut(
        id=decisao.id,
        capitulo_id=decisao.capitulo_id,
        pergunta=decisao.pergunta,
        opcoes=[OpcaoOut(texto=t, votos=v) for t, v in zip(decisao.opcoes, votos)],
        total_votos=sum(votos),
        ja_votei=meu is not None,
        minha_opcao=meu.opcao if meu else None,
        encerrada=jornada.encerrada(decisao.capitulo_id),
        vencedora=jornada.vencedora(decisao.capitulo_id),
        prazo=_com_fuso(decisao.prazo),
    )


def criar_decisao(db: Session, user: User, capitulo_id: int, dados: DecisaoCreate) -> DecisaoOut:
    capitulo = db.get(Capitulo, capitulo_id)
    if not capitulo:
        raise HTTPException(status_code=404, detail="capítulo não encontrado")
    historia = db.get(Historia, capitulo.historia_id)
    if historia.autor_id != user.id:
        raise HTTPException(status_code=403, detail="só o autor da história cria a decisão")
    if dados.prazo <= _agora():
        raise HTTPException(status_code=422, detail="o prazo precisa estar no futuro")
    if db.scalar(select(Decisao.id).where(Decisao.capitulo_id == capitulo_id)):
        raise HTTPException(status_code=409, detail="este capítulo já tem uma decisão")

    decisao = Decisao(
        capitulo_id=capitulo_id,
        pergunta=dados.pergunta,
        opcoes=dados.opcoes,
        prazo=dados.prazo,
    )
    db.add(decisao)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="este capítulo já tem uma decisão")
    jornada.abrir_decisao(capitulo_id, decisao.opcoes)
    return _out(db, user, decisao)


def obter(db: Session, user: User, decisao_id: int) -> DecisaoOut:
    return _out(db, user, _decisao(db, decisao_id))


def votar(db: Session, user: User, decisao_id: int, opcao: int) -> DecisaoOut:
    decisao = _decisao(db, decisao_id)
    if not 0 <= opcao < len(decisao.opcoes):
        raise HTTPException(status_code=422, detail="opção inválida")
    sincronizar(db, decisao)
    if decisao.prazo <= _agora():
        raise HTTPException(status_code=409, detail="votação encerrada")
    if db.get(Voto, (decisao_id, user.id)):
        raise HTTPException(status_code=409, detail="você já votou")
    db.add(Voto(decisao_id=decisao_id, user_id=user.id, opcao=opcao))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # duas requests simultâneas: a outra venceu
        raise HTTPException(status_code=409, detail="você já votou")
    em_alta.voto(db.get(Capitulo, decisao.capitulo_id).historia_id)
    return _out(db, user, decisao)


# ---- Capítulos (versão mínima; a issue de Quadrinhos completa) ----


def criar_capitulo(
    db: Session, user: User, historia_id: int, dados: CapituloCreate
) -> Capitulo:
    historia = db.get(Historia, historia_id)
    if not historia:
        raise HTTPException(status_code=404, detail="história não encontrada")
    if historia.autor_id != user.id:
        raise HTTPException(status_code=403, detail="só o autor publica capítulos")

    ja_tem = db.scalar(
        select(func.count()).select_from(Capitulo).where(Capitulo.historia_id == historia_id)
    )
    if dados.pai_id is None:
        if dados.opcao_origem is not None:
            raise HTTPException(status_code=422, detail="opcao_origem exige pai_id")
        if ja_tem:
            raise HTTPException(status_code=409, detail="a história já tem capítulo inicial")
    else:
        pai = db.get(Capitulo, dados.pai_id)
        if not pai or pai.historia_id != historia_id:
            raise HTTPException(status_code=404, detail="capítulo anterior não encontrado")
        decisao = db.scalar(select(Decisao).where(Decisao.capitulo_id == pai.id))
        if not decisao:
            raise HTTPException(status_code=409, detail="o capítulo anterior não tem decisão")
        sincronizar(db, decisao)
        if not jornada.encerrada(pai.id):
            raise HTTPException(status_code=409, detail="a votação ainda está aberta")
        vencedora = jornada.vencedora(pai.id)
        if vencedora is None:
            raise HTTPException(status_code=409, detail="a votação terminou sem votos")
        if dados.opcao_origem != vencedora:
            raise HTTPException(
                status_code=409, detail=f"a opção vencedora foi {vencedora}"
            )
        if jornada.no(pai.id).filhos.get(vencedora) is not None:
            raise HTTPException(status_code=409, detail="essa opção já tem capítulo")

    capitulo = Capitulo(
        historia_id=historia_id,
        numero=ja_tem + 1,
        titulo=dados.titulo,
        texto=dados.texto,
        imagem_url=dados.paginas[0] if dados.paginas else None,
        pai_id=dados.pai_id,
        opcao_origem=dados.opcao_origem,
    )
    db.add(capitulo)
    db.flush()
    db.add_all(
        Pagina(capitulo_id=capitulo.id, ordem=i, imagem_url=url)
        for i, url in enumerate(dados.paginas, start=1)
    )
    # capítulo novo vira post no feed de quem segue o artista
    post = Post(
        autor_id=user.id,
        texto=f"Novo capítulo de {historia.titulo}: {capitulo.titulo}",
        imagem_url=capitulo.imagem_url,
        historia_id=historia.id,
    )
    db.add(post)
    db.commit()
    tags.indexar_post(db, post)
    service_em_alta.registrar_post(post)
    jornada.adicionar_capitulo(capitulo.id, historia_id, dados.pai_id, dados.opcao_origem)
    return capitulo


def montar_jornada(db: Session, historia_id: int) -> JornadaOut:
    historia = db.get(Historia, historia_id)
    if not historia:
        raise HTTPException(status_code=404, detail="história não encontrada")

    caminho = jornada.caminho(historia_id)
    # só o último nó pode estar com a votação vencida e ainda não fechada (um nó com
    # filho publicado já foi fechado); fecha e recalcula
    if caminho and caminho[-1].tem_decisao and not caminho[-1].encerrada:
        decisao = db.scalar(select(Decisao).where(Decisao.capitulo_id == caminho[-1].capitulo_id))
        sincronizar(db, decisao)
        caminho = jornada.caminho(historia_id)

    ids = [no.capitulo_id for no in caminho]
    capitulos = {c.id: c for c in db.scalars(select(Capitulo).where(Capitulo.id.in_(ids)))}
    decisoes = {
        d.capitulo_id: d
        for d in db.scalars(select(Decisao).where(Decisao.capitulo_id.in_(ids)))
    }

    passos = []
    for no in caminho:
        cap = capitulos[no.capitulo_id]
        decisao_out = None
        if no.tem_decisao:
            d = decisoes[no.capitulo_id]
            votos = no.votos_finais if no.encerrada else _votos_por_opcao(db, d)
            vencedora = no.vencedora
            decisao_out = DecisaoJornadaOut(
                id=d.id,
                pergunta=d.pergunta,
                prazo=_com_fuso(d.prazo),
                encerrada=no.encerrada,
                opcoes=[
                    OpcaoJornadaOut(
                        indice=i, texto=t, votos=votos[i], escolhida=(i == vencedora)
                    )
                    for i, t in enumerate(no.opcoes)
                ],
            )
        passos.append(
            PassoOut(
                capitulo_id=cap.id, numero=cap.numero, titulo=cap.titulo, decisao=decisao_out
            )
        )
    return JornadaOut(historia_id=historia_id, titulo=historia.titulo, caminho=passos)
