"""Testes autorais das tags (issue #13): casos que o CONTRATO.md não especifica.

O principal: o índice invertido do core/ precisa acompanhar editar e apagar,
senão a tag continua "apontando" para um post que já não fala dela.
"""

from app.core.tags import IndiceTags, extrair_tags


def _textos(r):
    return [p["texto"] for p in r.json()["items"]]


def test_autoral_editar_post_tira_a_tag_antiga_do_indice(client, logar):
    # e se o autor EDITAR o post trocando a hashtag? a tag velha não pode sobrar
    ana = logar("ana")
    post = client.post("/posts", json={"texto": "meu rascunho #fantasia"}, headers=ana).json()
    assert client.get("/tags/fantasia/posts", headers=ana).json()["total"] == 1

    client.patch(f"/posts/{post['id']}", json={"texto": "agora é #scifi"}, headers=ana)

    assert client.get("/tags/fantasia/posts", headers=ana).json()["total"] == 0
    assert _textos(client.get("/tags/scifi/posts", headers=ana)) == ["agora é #scifi"]


def test_autoral_apagar_post_tira_do_indice(client, logar):
    ana = logar("ana")
    post = client.post("/posts", json={"texto": "#terror noite"}, headers=ana).json()
    client.delete(f"/posts/{post['id']}", headers=ana)

    r = client.get("/tags/terror/posts", headers=ana)
    assert r.status_code == 200
    assert r.json()["items"] == []
    assert client.get("/tags", headers=ana).json()["items"] == []


def test_autoral_tag_repetida_e_com_maiusculas_conta_uma_vez(client, logar):
    ana = logar("ana")
    client.post("/posts", json={"texto": "#Fantasia #fantasia #FANTASIA dragões"}, headers=ana)

    r = client.get("/tags/FANTASIA/posts", headers=ana)  # a busca também ignora caixa
    assert r.json()["total"] == 1
    assert len(r.json()["items"]) == 1
    assert client.get("/tags", headers=ana).json()["items"] == [{"tag": "fantasia", "contagem": 1}]


def test_autoral_explorar_filtra_por_tag_e_pagina(client, logar):
    ana = logar("ana")
    for t in ["um #sol", "dois #lua", "três #sol", "quatro #sol"]:
        client.post("/posts", json={"texto": t}, headers=ana)

    r = client.get("/explorar?tag=sol&offset=1&limit=1", headers=ana)
    assert r.json()["total"] == 3
    assert _textos(r) == ["três #sol"]
    assert client.get("/explorar?tag=%23sem espaco", headers=ana).status_code == 422
    assert client.get("/explorar?tag=sol").status_code == 401


def test_autoral_explorar_prioriza_interesses_do_usuario(client, logar):
    ana = logar("ana")
    bia = logar("bia")
    for t in ["velho #fantasia", "meio #scifi", "novo #terror"]:
        client.post("/posts", json={"texto": t}, headers=bia)

    # sem interesses: puro cronológico
    assert _textos(client.get("/explorar", headers=ana)) == [
        "novo #terror", "meio #scifi", "velho #fantasia"
    ]

    r = client.patch("/usuarios/eu", json={"tags_interesse": ["#FANTASIA", "fantasia", "scifi"]}, headers=ana)
    assert r.status_code == 200
    assert r.json()["tags_interesse"] == ["fantasia", "scifi"]  # normaliza e não duplica

    # interesses primeiro (mais novo antes), depois o resto; o total continua sendo todos
    r = client.get("/explorar", headers=ana)
    assert _textos(r) == ["meio #scifi", "velho #fantasia", "novo #terror"]
    assert r.json()["total"] == 3


def test_autoral_tags_de_interesse_invalidas_dao_422_e_nao_mexem_no_que_havia(client, logar):
    ana = logar("ana")
    client.patch("/usuarios/eu", json={"tags_interesse": ["sol"]}, headers=ana)

    assert client.patch("/usuarios/eu", json={"tags_interesse": ["com espaço"]}, headers=ana).status_code == 422
    assert client.patch("/usuarios/eu", json={"tags_interesse": ["ação"]}, headers=ana).status_code == 422
    assert client.patch("/usuarios/eu", json={"tags_interesse": [f"t{i}" for i in range(11)]}, headers=ana).status_code == 422
    assert client.patch("/usuarios/eu", json={"bio": "oi"}, headers=ana).json()["tags_interesse"] == ["sol"]
    assert client.patch("/usuarios/eu", json={"tags_interesse": []}, headers=ana).json()["tags_interesse"] == []


def test_autoral_post_de_capitulo_herda_as_tags_da_historia(client, logar):
    # só artista publica história: registra com tipo "artista" e faz login
    client.post("/auth/registro", json={"username": "ana", "name": "Ana", "password": "senha-forte-123", "tipo": "artista"})
    token = client.post("/auth/login", json={"username": "ana", "password": "senha-forte-123"}).json()["token"]
    ana = {"Authorization": f"Bearer {token}"}
    historia = client.post("/historias", json={"titulo": "Lua", "tags": ["Fantasia"]}, headers=ana)
    assert historia.status_code == 201, historia.text
    client.post(
        f"/historias/{historia.json()['id']}/capitulos",
        json={"titulo": "Início", "paginas": ["/seed/fantasia-torre.svg"]},
        headers=ana,
    )
    r = client.get("/tags/fantasia/posts", headers=ana)
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["historia_id"] == historia.json()["id"]


# ---- core/ puro: roda sem servidor ----


def test_autoral_core_extrair_tags():
    assert extrair_tags("oi #Sol e #sol, #lua_2! a#b #café &#39; ##x") == ["sol", "lua_2"]
    assert extrair_tags("sem tags") == []


def test_autoral_core_indice_substitui_e_ordena_ranking():
    indice = IndiceTags()
    indice.reconstruir([(1, ["b", "a"]), (2, ["b"]), (3, ["c"])])
    assert indice.mais_usadas(5) == [("b", 2), ("a", 1), ("c", 1)]  # empate: alfabética

    indice.indexar(2, ["c"])  # editado: sai de "b", entra em "c"
    assert indice.ids_da_tag("b") == {1}
    assert indice.ids_com_alguma(["b", "c"]) == {1, 2, 3}
    indice.remover(1)
    assert indice.ids_da_tag("a") == set()
    assert indice.mais_usadas(1) == [("c", 2)]
