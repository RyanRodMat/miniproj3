"""Casos do seed fake que o test_nucleo não cobre (guia 09).

O núcleo só confere os mínimos de contagem. Aqui conferimos o que faz a demo
parecer uma rede de verdade: senha, mistura de conteúdo, imagens que existem no
repo, tags coerentes, história com decisão aberta e idempotência.
"""

import re
import sys
from pathlib import Path

import pytest
from sqlalchemy import func, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import seed  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.models.capitulo import Capitulo  # noqa: E402
from app.models.decisao import Decisao  # noqa: E402
from app.models.follow import Follow  # noqa: E402
from app.models.historia import Historia  # noqa: E402
from app.models.interesse import Interesse  # noqa: E402
from app.models.like import Like  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.voto import Voto  # noqa: E402
from app.services.decisoes import _agora  # noqa: E402
from app.schemas.post import URL_PATTERN  # noqa: E402

PUBLIC_SEED = Path(__file__).resolve().parents[2] / "frontend" / "public" / "seed"
TAGS_VALIDAS = {"fantasia", "terror", "slice_of_life", "scifi", "aventura", "humor"}


@pytest.fixture()
def db(client):
    """Sessão com o banco zerado (o `client` recria as tabelas) e o seed aplicado."""
    with SessionLocal() as s:
        seed.seed_fake(s)
        yield s


def _contar(db, model) -> int:
    return db.scalar(select(func.count()).select_from(model)) or 0


def _token(client, username: str) -> dict:
    r = client.post("/auth/login", json={"username": username, "password": seed.SENHA_SEED})
    assert r.status_code == 200, username
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_seed_mistura_artistas_e_leitores(db):
    tipos = dict(db.execute(select(User.tipo, func.count()).group_by(User.tipo)).all())
    assert tipos["artista"] >= 5
    assert tipos["leitor"] >= 5
    assert sum(tipos.values()) >= 20


def test_todos_os_usuarios_logam_com_a_senha_do_seed(db, client):
    for username in db.scalars(select(User.username)):
        _token(client, username)


def test_posts_misturam_texto_e_arte_e_a_arte_aparece_na_api(db, client):
    com_arte = db.scalar(select(func.count()).select_from(Post).where(Post.imagem_url.is_not(None)))
    so_texto = db.scalar(select(func.count()).select_from(Post).where(Post.imagem_url.is_(None)))
    assert com_arte >= 20
    assert so_texto >= 20

    r = client.get("/posts?limit=100", headers=_token(client, "leo_leitor"))
    assert r.status_code == 200
    assert any(p["imagem_url"] for p in r.json()["items"])


def test_imagens_do_seed_existem_no_repo_e_passam_na_validacao(db):
    urls = set(db.scalars(select(Post.imagem_url).where(Post.imagem_url.is_not(None))))
    urls |= set(db.scalars(select(Capitulo.imagem_url).where(Capitulo.imagem_url.is_not(None))))
    assert urls
    for url in urls:
        assert re.match(URL_PATTERN, url) and len(url) <= 300
        assert url.startswith("/seed/")  # nunca /uploads: some no deploy
        assert (PUBLIC_SEED / url.removeprefix("/seed/")).is_file(), url


def test_follows_e_curtidas_nao_tem_auto_relacao_nem_ponta_solta(db):
    assert _contar(db, Follow) >= 20
    assert _contar(db, Like) >= 30
    assert db.scalar(select(func.count()).select_from(Follow).where(Follow.follower_id == Follow.followed_id)) == 0

    ids_user = set(db.scalars(select(User.id)))
    for f in db.scalars(select(Follow)):
        assert f.follower_id in ids_user and f.followed_id in ids_user

    autor_do_post = dict(db.execute(select(Post.id, Post.autor_id)).all())
    for like in db.scalars(select(Like)):
        assert like.liker_id in ids_user
        assert autor_do_post[like.liked_post_id] != like.liker_id  # ninguém curte o próprio


def test_tags_de_interesse_sao_coerentes(db):
    interesses: dict[int, set[str]] = {}
    for i in db.scalars(select(Interesse)):
        assert i.tag in TAGS_VALIDAS
        interesses.setdefault(i.user_id, set()).add(i.tag)
    # todo usuário tem pelo menos uma tag
    assert set(interesses) == set(db.scalars(select(User.id)))
    # os 4 gêneros do nicho aparecem
    assert {"fantasia", "terror", "slice_of_life", "scifi"} <= set().union(*interesses.values())

    # hashtag no post só se o autor tem aquela tag de interesse
    for post in db.scalars(select(Post)):
        for tag in re.findall(r"#(\w+)", post.texto):
            assert tag in interesses[post.autor_id], (post.autor.username, tag)


def test_historias_tem_capitulos_decisoes_votadas_e_uma_em_aberto(db):
    assert 1 <= _contar(db, Historia) <= 2
    abertas = db.scalar(select(func.count()).select_from(Decisao).where(Decisao.prazo > _agora()))
    assert abertas >= 1
    assert db.scalar(select(func.count()).select_from(Decisao).where(Decisao.prazo <= _agora())) >= 1

    for historia in db.scalars(select(Historia)):
        caps = list(db.scalars(select(Capitulo).where(Capitulo.historia_id == historia.id).order_by(Capitulo.numero)))
        assert len(caps) >= 2
        assert [c.numero for c in caps] == list(range(1, len(caps) + 1))
        tags_autor = set(db.scalars(select(Interesse.tag).where(Interesse.user_id == historia.autor_id)))
        assert historia.tag in tags_autor

    for decisao in db.scalars(select(Decisao)):
        assert len(decisao.opcoes) >= 2
        votos = list(db.scalars(select(Voto).where(Voto.decisao_id == decisao.id)))
        assert votos, "toda decisão (inclusive a aberta) já tem voto, para a demo não ficar vazia"
        assert all(0 <= v.opcao < len(decisao.opcoes) for v in votos)


def test_so_a_ultima_decisao_de_cada_historia_esta_aberta(db):
    for historia in db.scalars(select(Historia)):
        decisoes = list(
            db.scalars(
                select(Decisao)
                .join(Capitulo, Capitulo.id == Decisao.capitulo_id)
                .where(Capitulo.historia_id == historia.id)
                .order_by(Capitulo.numero)
            )
        )
        assert [d.prazo > _agora() for d in decisoes] == [False] * (len(decisoes) - 1) + [True]


def test_capitulos_seguem_a_opcao_vencedora_e_o_mapa_da_jornada_funciona(db, client):
    """O seed tem que respeitar a regra da jornada: o capítulo seguinte nasce da opção vencedora."""
    for historia in db.scalars(select(Historia)):
        caps = list(db.scalars(select(Capitulo).where(Capitulo.historia_id == historia.id).order_by(Capitulo.numero)))
        assert caps[0].pai_id is None and caps[0].opcao_origem is None
        for anterior, cap in zip(caps, caps[1:]):
            decisao = db.scalar(select(Decisao).where(Decisao.capitulo_id == anterior.id))
            contagem = [0] * len(decisao.opcoes)
            for v in db.scalars(select(Voto).where(Voto.decisao_id == decisao.id)):
                contagem[v.opcao] += 1
            vencedora = max(range(len(contagem)), key=lambda i: (contagem[i], -i))
            assert (cap.pai_id, cap.opcao_origem) == (anterior.id, vencedora)

        r = client.get(f"/historias/{historia.id}/jornada", headers=_token(client, "leo_leitor"))
        assert r.status_code == 200
        assert [p["numero"] for p in r.json()["caminho"]] == [c.numero for c in caps]


def test_autor_da_historia_nao_vota_nela(db):
    for historia in db.scalars(select(Historia)):
        votos_do_autor = db.scalar(
            select(func.count())
            .select_from(Voto)
            .join(Decisao, Decisao.id == Voto.decisao_id)
            .join(Capitulo, Capitulo.id == Decisao.capitulo_id)
            .where(Capitulo.historia_id == historia.id, Voto.user_id == historia.autor_id)
        )
        assert votos_do_autor == 0


def test_seed_e_idempotente_rodar_de_novo_nao_duplica(db):
    antes = {m: _contar(db, m) for m in (User, Post, Follow, Like, Historia, Voto)}
    assert seed.seed_fake(db) == {}
    assert antes == {m: _contar(db, m) for m in antes}


def test_feed_de_leitor_do_seed_nao_nasce_vazio(db, client):
    r = client.get("/feed", headers=_token(client, "carol_le"))
    assert r.status_code == 200
    assert r.json()["total"] > 0
