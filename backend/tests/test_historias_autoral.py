"""Casos de borda de Histórias e Capítulos que o CONTRATO.md não especifica (guia 09)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import text

HIST = {"titulo": "Torre Torta", "sinopse": "s", "tags": ["fantasia"]}
CAP = {"titulo": "O começo", "texto": "t", "paginas": ["/uploads/p1.png", "/uploads/p2.png"]}


def _artista(client, username):
    r = client.post(
        "/auth/registro",
        json={"username": username, "name": "A", "password": "senha-forte-123", "tipo": "artista"},
    )
    assert r.status_code == 201
    r = client.post("/auth/login", json={"username": username, "password": "senha-forte-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _seguinte(client, autor, leitor, hid, cap, **dados):
    """Publica o capítulo seguinte: abre a decisão, 1 voto na opção 0, vence o prazo e publica."""
    prazo = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    d = client.post(
        f"/capitulos/{cap['id']}/decisao",
        json={"pergunta": "?", "opcoes": ["a", "b"], "prazo": prazo},
        headers=autor,
    ).json()
    client.post(f"/decisoes/{d['id']}/votar", json={"opcao": 0}, headers=leitor)
    from app.db import engine

    passado = (datetime.now(timezone.utc) - timedelta(minutes=1)).replace(tzinfo=None)
    with engine.begin() as conn:
        conn.execute(text("UPDATE decisoes SET prazo = :p WHERE id = :i"), {"p": passado, "i": d["id"]})
    return client.post(
        f"/historias/{hid}/capitulos",
        json={**CAP, "pai_id": cap["id"], "opcao_origem": 0, **dados},
        headers=autor,
    )


def test_so_artista_cria_historia_e_exige_login(client, logar):
    leitor = logar("leitora")
    assert client.post("/historias", json=HIST, headers=leitor).status_code == 403
    assert client.post("/historias", json=HIST).status_code == 401
    assert client.get("/historias/1").status_code == 401


def test_so_o_autor_publica_capitulo_na_sua_historia(client, logar):
    ana = _artista(client, "ana")
    bia = _artista(client, "bia")
    hid = client.post("/historias", json=HIST, headers=ana).json()["id"]

    assert client.post(f"/historias/{hid}/capitulos", json=CAP, headers=bia).status_code == 403
    assert client.post(f"/historias/{hid}/capitulos", json=CAP, headers=logar("leo")).status_code == 403
    assert client.get(f"/historias/{hid}", headers=ana).json()["capitulos"] == []
    assert client.post("/historias/999/capitulos", json=CAP, headers=ana).status_code == 404


def test_capitulos_numerados_em_ordem_e_com_paginas_em_sequencia(client, logar):
    ana = _artista(client, "ana")
    leo = logar("leo")
    hid = client.post("/historias", json=HIST, headers=ana).json()["id"]
    c1 = client.post(f"/historias/{hid}/capitulos", json={**CAP, "titulo": "um"}, headers=ana).json()
    c2 = _seguinte(client, ana, leo, hid, c1, titulo="dois").json()
    _seguinte(client, ana, leo, hid, c2, titulo="tres")

    corpo = client.get(f"/historias/{hid}", headers=ana).json()
    assert [(c["numero"], c["titulo"]) for c in corpo["capitulos"]] == [(1, "um"), (2, "dois"), (3, "tres")]
    assert corpo["autor"]["username"] == "ana"

    cap = client.get(f"/historias/{hid}/capitulos/2", headers=ana).json()
    assert cap["paginas"] == ["/uploads/p1.png", "/uploads/p2.png"]
    assert client.get(f"/historias/{hid}/capitulos/9", headers=ana).status_code == 404


def test_pagina_com_url_perigosa_e_422_e_capitulo_so_de_texto_vale(client):
    ana = _artista(client, "ana")
    hid = client.post("/historias", json=HIST, headers=ana).json()["id"]
    r = client.post(f"/historias/{hid}/capitulos", json={**CAP, "paginas": ["javascript:alert(1)"]}, headers=ana)
    assert r.status_code == 422
    assert client.get(f"/historias/{hid}", headers=ana).json()["capitulos"] == []

    r = client.post(f"/historias/{hid}/capitulos", json={"titulo": "só texto", "texto": "oi"}, headers=ana)
    assert r.status_code == 201
    assert client.get(f"/historias/{hid}/capitulos/1", headers=ana).json()["paginas"] == []


def test_tags_sao_normalizadas_e_historia_sem_tag_vale(client):
    ana = _artista(client, "ana")
    r = client.post("/historias", json={**HIST, "tags": ["Fantasia", "fantasia", "#Slice Of Life", " "]}, headers=ana)
    assert r.status_code == 201
    assert r.json()["tags"] == ["fantasia", "slice_of_life"]
    assert client.post("/historias", json={"titulo": "x"}, headers=ana).json()["tags"] == []
    assert client.post("/historias", json={**HIST, "tags": list("abcdef")}, headers=ana).status_code == 422


def test_publicar_capitulo_gera_post_no_feed_de_quem_segue(client, logar):
    ana = _artista(client, "ana")
    leo = logar("leo")
    client.post("/usuarios/ana/follow", headers=leo)
    hid = client.post("/historias", json=HIST, headers=ana).json()["id"]
    client.post(f"/historias/{hid}/capitulos", json=CAP, headers=ana)

    itens = client.get("/feed", headers=leo).json()["items"]
    assert len(itens) == 1
    assert itens[0]["texto"] == "Novo capítulo de Torre Torta: O começo"
    assert itens[0]["historia_id"] == hid
    assert itens[0]["imagem_url"] == "/uploads/p1.png"
