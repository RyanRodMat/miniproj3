"""Casos de borda de Posts que o CONTRATO.md não especifica (guia 09)."""


def test_post_exige_login(client):
    assert client.post("/posts", json={"texto": "oi"}).status_code == 401
    assert client.get("/posts/1").status_code == 401


def test_post_vazio_ou_enorme_e_422(client, logar):
    ana = logar("ana")
    assert client.post("/posts", json={"texto": ""}, headers=ana).status_code == 422
    assert client.post("/posts", json={"texto": "x" * 2001}, headers=ana).status_code == 422


def test_post_de_arte_devolve_imagem_e_autor(client, logar):
    ana = logar("ana", "Ana")
    r = client.post(
        "/posts",
        json={"texto": "novo desenho", "imagem_url": "https://exemplo.com/a.png"},
        headers=ana,
    )
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["imagem_url"] == "https://exemplo.com/a.png"
    assert corpo["autor"]["username"] == "ana"
    assert "password_hash" not in corpo["autor"]

    # post só de texto: imagem_url nula
    r = client.post("/posts", json={"texto": "só texto"}, headers=ana)
    assert r.json()["imagem_url"] is None


def test_imagem_url_rejeita_esquema_perigoso(client, logar):
    ana = logar("ana")
    r = client.post(
        "/posts", json={"texto": "x", "imagem_url": "javascript:alert(1)"}, headers=ana
    )
    assert r.status_code == 422


def test_so_o_autor_edita_e_post_inexistente_e_404(client, logar):
    ana = logar("ana")
    bia = logar("bia")
    post_id = client.post("/posts", json={"texto": "meu"}, headers=ana).json()["id"]

    r = client.patch(f"/posts/{post_id}", json={"texto": "invadido"}, headers=bia)
    assert r.status_code == 403
    assert client.get(f"/posts/{post_id}", headers=ana).json()["texto"] == "meu"

    assert client.patch("/posts/9999", json={"texto": "x"}, headers=ana).status_code == 404
    assert client.delete("/posts/9999", headers=ana).status_code == 404


def test_patch_pode_remover_imagem_e_nao_aceita_texto_nulo(client, logar):
    ana = logar("ana")
    post_id = client.post(
        "/posts", json={"texto": "t", "imagem_url": "/uploads/a.png"}, headers=ana
    ).json()["id"]

    r = client.patch(f"/posts/{post_id}", json={"imagem_url": None}, headers=ana)
    assert r.status_code == 200
    assert r.json()["imagem_url"] is None
    assert r.json()["texto"] == "t"  # campo ausente não é alterado

    r = client.patch(f"/posts/{post_id}", json={"texto": None}, headers=ana)
    assert r.status_code == 422
