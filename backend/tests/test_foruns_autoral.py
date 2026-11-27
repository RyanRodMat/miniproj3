"""Fóruns: criar, entrar/sair e postar (issue #14)."""


def _criar(client, headers, nome="Anatomia", descricao=""):
    return client.post("/foruns", json={"nome": nome, "descricao": descricao}, headers=headers)


def test_criar_forum_nome_unico_e_criador_vira_membro(client, logar):
    ana, bia = logar("ana"), logar("bia")
    r = _criar(client, ana, "Anatomia", "dicas de corpo")
    assert r.status_code == 201
    f = r.json()
    assert (f["nome"], f["membros"], f["sou_membro"]) == ("Anatomia", 1, True)

    assert _criar(client, bia, "Anatomia").status_code == 409
    assert _criar(client, bia, "  anatomia ").status_code == 409  # sem diferenciar caixa/espaços
    assert _criar(client, bia, "   ").status_code == 422
    assert client.post("/foruns", json={}, headers=ana).status_code == 422
    assert client.post("/foruns", json={"nome": "x"}).status_code == 401


def test_listar_foruns_pagina_e_mostra_se_sou_membro(client, logar):
    ana, bia = logar("ana"), logar("bia")
    for nome in ("A", "B", "C"):
        _criar(client, ana, nome)

    r = client.get("/foruns?offset=0&limit=2", headers=bia).json()
    assert r["total"] == 3
    assert [f["nome"] for f in r["items"]] == ["C", "B"]  # mais novo primeiro
    assert not any(f["sou_membro"] for f in r["items"])
    assert client.get("/foruns?limit=0", headers=bia).status_code == 422


def test_entrar_e_sair_sao_idempotentes(client, logar):
    ana, bia = logar("ana"), logar("bia")
    fid = _criar(client, ana).json()["id"]

    assert client.post(f"/foruns/{fid}/entrar", headers=bia).status_code == 204
    assert client.post(f"/foruns/{fid}/entrar", headers=bia).status_code == 204
    f = client.get(f"/foruns/{fid}", headers=bia).json()
    assert (f["membros"], f["sou_membro"]) == (2, True)

    assert client.post(f"/foruns/{fid}/sair", headers=bia).status_code == 204
    assert client.post(f"/foruns/{fid}/sair", headers=bia).status_code == 204
    f = client.get(f"/foruns/{fid}", headers=bia).json()
    assert (f["membros"], f["sou_membro"]) == (1, False)

    assert client.post("/foruns/999/entrar", headers=bia).status_code == 404
    assert client.post("/foruns/999/sair", headers=bia).status_code == 404
    assert client.get("/foruns/999", headers=bia).status_code == 404


def test_so_membro_posta_e_posts_listam_do_mais_novo(client, logar):
    ana, bia = logar("ana"), logar("bia")
    fid = _criar(client, ana).json()["id"]

    r = client.post(f"/foruns/{fid}/posts", json={"texto": "oi"}, headers=bia)
    assert r.status_code == 403

    client.post(f"/foruns/{fid}/entrar", headers=bia)
    assert client.post(f"/foruns/{fid}/posts", json={"texto": "primeiro"}, headers=bia).status_code == 201
    assert client.post(f"/foruns/{fid}/posts", json={"texto": "segundo"}, headers=ana).status_code == 201
    assert client.post(f"/foruns/{fid}/posts", json={"texto": "  "}, headers=ana).status_code == 422
    assert client.post("/foruns/999/posts", json={"texto": "x"}, headers=ana).status_code == 404

    r = client.get(f"/foruns/{fid}/posts?limit=1", headers=bia).json()
    assert r["total"] == 2
    assert r["items"][0]["texto"] == "segundo"
    assert r["items"][0]["autor"]["username"] == "ana"

    # quem sai não posta mais, mas os posts continuam lá
    client.post(f"/foruns/{fid}/sair", headers=bia)
    assert client.post(f"/foruns/{fid}/posts", json={"texto": "x"}, headers=bia).status_code == 403
    assert client.get(f"/foruns/{fid}/posts", headers=bia).json()["total"] == 2
    assert client.get("/foruns/999/posts", headers=bia).status_code == 404


def test_posts_do_forum_nao_entram_no_feed_nem_em_posts(client, logar):
    ana, bia = logar("ana"), logar("bia")
    client.post("/usuarios/ana/follow", headers=bia)
    fid = _criar(client, ana).json()["id"]
    client.post(f"/foruns/{fid}/posts", json={"texto": "só no fórum"}, headers=ana)

    assert client.get("/feed", headers=bia).json()["items"] == []
    assert client.get("/posts", headers=bia).json()["total"] == 0
    assert client.get("/em-alta", headers=bia).json()["total"] == 0
    assert client.get("/usuarios/ana/posts", headers=bia).json()["total"] == 0
