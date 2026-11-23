"""Perfil: o que dá para testar sem Posts/Follow. (O teste do núcleo,
test_perfil_editavel, continua skipped: ele lista os posts do usuário.)"""


def test_editar_e_ler_perfil(client, logar):
    ana = logar("ana", "Ana")

    r = client.patch(
        "/usuarios/eu",
        json={"bio": "oi, sou a ana", "avatar_url": "https://exemplo.com/a.png"},
        headers=ana,
    )
    assert r.status_code == 200

    # quem olha o perfil é outra pessoa
    bia = logar("bia")
    corpo = client.get("/usuarios/ana", headers=bia).json()
    assert corpo["bio"] == "oi, sou a ana"
    assert corpo["avatar_url"] == "https://exemplo.com/a.png"
    assert corpo["tipo"] == "leitor"
    assert "password_hash" not in corpo


def test_perfil_exige_login(client, logar):
    logar("ana")
    assert client.patch("/usuarios/eu", json={"bio": "x"}).status_code == 401
    assert client.get("/usuarios/ana").status_code == 401


def test_perfil_inexistente_e_404(client, logar):
    ana = logar("ana")
    assert client.get("/usuarios/fantasma", headers=ana).status_code == 404


def test_patch_parcial_nao_apaga_o_resto_e_string_vazia_limpa(client, logar):
    ana = logar("ana")
    client.patch(
        "/usuarios/eu", json={"bio": "bio", "avatar_url": "/img/a.png"}, headers=ana
    )

    r = client.patch("/usuarios/eu", json={"bio": "nova bio"}, headers=ana)
    assert r.json()["bio"] == "nova bio"
    assert r.json()["avatar_url"] == "/img/a.png"  # não foi enviado, não mudou

    r = client.patch("/usuarios/eu", json={"avatar_url": ""}, headers=ana)
    assert r.json()["avatar_url"] == ""


def test_patch_valida_limites_e_nao_deixa_trocar_tipo_ou_username(client, logar):
    ana = logar("ana")
    assert client.patch("/usuarios/eu", json={"bio": "x" * 281}, headers=ana).status_code == 422
    assert client.patch("/usuarios/eu", json={"bio": None}, headers=ana).status_code == 422
    r = client.patch(
        "/usuarios/eu", json={"avatar_url": "javascript:alert(1)"}, headers=ana
    )
    assert r.status_code == 422

    # campos fora do schema são ignorados: ninguém vira artista nem troca de nome por aqui
    r = client.patch(
        "/usuarios/eu", json={"tipo": "artista", "username": "outro"}, headers=ana
    )
    assert r.status_code == 200
    assert r.json()["tipo"] == "leitor"
    assert r.json()["username"] == "ana"


def test_stats_continua_acessivel(client):
    # /usuarios/stats não pode ser engolida por /usuarios/{username}
    assert client.get("/usuarios/stats").status_code == 200
