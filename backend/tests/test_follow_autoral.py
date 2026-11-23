"""Casos de borda de Follow que o CONTRATO.md não especifica (guia 09)."""


def test_follow_exige_login(client, logar):
    logar("bia")
    assert client.post("/usuarios/bia/follow").status_code == 401
    assert client.get("/usuarios/bia").status_code == 401


def test_nao_segue_a_si_mesmo(client, logar):
    ana = logar("ana")
    assert client.post("/usuarios/ana/follow", headers=ana).status_code == 422
    assert client.get("/usuarios/ana", headers=ana).json()["seguindo"] == 0


def test_seguir_usuario_inexistente_e_404(client, logar):
    ana = logar("ana")
    assert client.post("/usuarios/fantasma/follow", headers=ana).status_code == 404
    assert client.delete("/usuarios/fantasma/follow", headers=ana).status_code == 404
    assert client.get("/usuarios/fantasma", headers=ana).status_code == 404


def test_deixar_de_seguir_quem_nao_segue_e_idempotente(client, logar):
    ana = logar("ana")
    logar("bia")
    assert client.delete("/usuarios/bia/follow", headers=ana).status_code == 204
    assert client.get("/usuarios/bia", headers=ana).json()["seguidores"] == 0


def test_follow_e_direcional_e_eu_sigo_depende_de_quem_olha(client, logar):
    ana = logar("ana")
    bia = logar("bia")
    client.post("/usuarios/bia/follow", headers=ana)

    # ana segue bia, mas bia não segue ana
    assert client.get("/usuarios/bia", headers=ana).json()["eu_sigo"] is True
    assert client.get("/usuarios/ana", headers=bia).json()["eu_sigo"] is False
    assert client.get("/usuarios/ana", headers=ana).json()["seguindo"] == 1
    assert client.get("/usuarios/ana", headers=ana).json()["seguidores"] == 0


def test_perfil_nao_vaza_hash_da_senha(client, logar):
    ana = logar("ana")
    corpo = client.get("/usuarios/ana", headers=ana).json()
    assert "password_hash" not in corpo and "password" not in corpo


def test_stats_continua_acessivel(client):
    # /usuarios/stats não pode ser engolida por /usuarios/{username}
    assert client.get("/usuarios/stats").status_code == 200
