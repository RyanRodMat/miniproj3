from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.forum import Forum, ForumMembro, ForumPost
from app.models.user import User
from app.schemas.forum import ForumCreate, ForumOut, ForumPostCreate


def buscar(db: Session, forum_id: int) -> Forum:
    forum = db.get(Forum, forum_id)
    if not forum:
        raise HTTPException(status_code=404, detail="fórum não encontrado")
    return forum


def _out_em_lote(db: Session, user: User, foruns: list[Forum]) -> list[ForumOut]:
    ids = [f.id for f in foruns]
    membros = dict(
        db.execute(
            select(ForumMembro.forum_id, func.count())
            .where(ForumMembro.forum_id.in_(ids))
            .group_by(ForumMembro.forum_id)
        ).all()
    )
    meus = set(
        db.scalars(
            select(ForumMembro.forum_id).where(
                ForumMembro.user_id == user.id, ForumMembro.forum_id.in_(ids)
            )
        )
    )
    return [
        ForumOut(
            id=f.id,
            nome=f.nome,
            descricao=f.descricao,
            criador_id=f.criador_id,
            created_at=f.created_at,
            membros=membros.get(f.id, 0),
            sou_membro=f.id in meus,
        )
        for f in foruns
    ]


def out(db: Session, user: User, forum: Forum) -> ForumOut:
    return _out_em_lote(db, user, [forum])[0]


def criar(db: Session, user: User, dados: ForumCreate) -> Forum:
    existe = db.scalar(select(Forum.id).where(func.lower(Forum.nome) == dados.nome.lower()))
    if existe:
        raise HTTPException(status_code=409, detail="já existe um fórum com esse nome")
    forum = Forum(nome=dados.nome, descricao=dados.descricao, criador_id=user.id)
    db.add(forum)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="já existe um fórum com esse nome")
    # quem cria o fórum já participa dele
    db.add(ForumMembro(forum_id=forum.id, user_id=user.id))
    db.commit()
    db.refresh(forum)
    return forum


def listar(db: Session, user: User, offset: int, limit: int) -> tuple[list[ForumOut], int]:
    """Mais recentes primeiro (empate: maior id)."""
    total = db.scalar(select(func.count()).select_from(Forum)) or 0
    foruns = list(
        db.scalars(
            select(Forum).order_by(Forum.created_at.desc(), Forum.id.desc()).offset(offset).limit(limit)
        )
    )
    return _out_em_lote(db, user, foruns), total


def entrar(db: Session, user: User, forum_id: int) -> None:
    forum = buscar(db, forum_id)
    if db.get(ForumMembro, (forum.id, user.id)):
        return  # idempotente
    db.add(ForumMembro(forum_id=forum.id, user_id=user.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # duas requests simultâneas: a outra já criou


def sair(db: Session, user: User, forum_id: int) -> None:
    forum = buscar(db, forum_id)
    membro = db.get(ForumMembro, (forum.id, user.id))
    if membro:
        db.delete(membro)
        db.commit()


def postar(db: Session, user: User, forum_id: int, dados: ForumPostCreate) -> ForumPost:
    forum = buscar(db, forum_id)
    if not db.get(ForumMembro, (forum.id, user.id)):
        raise HTTPException(status_code=403, detail="entre no fórum para postar")
    post = ForumPost(forum_id=forum.id, autor_id=user.id, texto=dados.texto)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def listar_posts(
    db: Session, forum_id: int, offset: int, limit: int
) -> tuple[list[ForumPost], int]:
    forum = buscar(db, forum_id)
    filtro = ForumPost.forum_id == forum.id
    total = db.scalar(select(func.count()).select_from(ForumPost).where(filtro)) or 0
    posts = list(
        db.scalars(
            select(ForumPost)
            .where(filtro)
            .order_by(ForumPost.created_at.desc(), ForumPost.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return posts, total
