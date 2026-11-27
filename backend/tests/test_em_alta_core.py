"""Testes do core/em_alta.py: estrutura pura, sem servidor."""

from app.core.em_alta import EmAlta, pontuacao

H = 3600.0


def test_pontuacao_pesa_comentario_e_voto_mais_que_curtida():
    assert pontuacao(0, 1, 0, 0) == 2 * pontuacao(1, 0, 0, 0)
    assert pontuacao(0, 0, 1, 0) == 3 * pontuacao(1, 0, 0, 0)
    # a fórmula da issue: (1 + 2·1 + 3·1) / (0 + 2)^1.5
    assert abs(pontuacao(1, 1, 1, 0) - 6 / 2**1.5) < 1e-9


def test_pontuacao_cai_com_o_tempo_e_aguenta_relogio_torto():
    assert pontuacao(5, 0, 0, 24) < pontuacao(5, 0, 0, 1)
    assert pontuacao(5, 0, 0, -3) == pontuacao(5, 0, 0, 0)


def test_top_ordena_por_score_e_respeita_k():
    e = EmAlta()
    agora = 100 * H
    for pid in (1, 2, 3):
        e.registrar(pid, agora)
    e.curtida(2, +5)
    e.comentario(3, +1)  # vale 2 curtidas
    assert e.top(3, agora) == [2, 3, 1]
    assert e.top(2, agora) == [2, 3]
    assert e.top(0, agora) == []


def test_post_novo_com_pouco_engajamento_passa_o_velho_famoso():
    e = EmAlta()
    agora = 1000 * H
    e.registrar(1, agora - 72 * H)  # velho, 20 curtidas
    e.registrar(2, agora - 1 * H)  # novo, 4 curtidas
    e.curtida(1, +20)
    e.curtida(2, +4)
    assert e.top(2, agora) == [2, 1]


def test_empate_vence_o_mais_novo():
    e = EmAlta()
    e.registrar(1, 10 * H)
    e.registrar(2, 20 * H)
    # mesmo engajamento, mas o 2 é mais novo => já tem score maior; força empate exato
    assert e.top(2, 20 * H)[0] == 2
    e2 = EmAlta()
    e2.registrar(1, 0)
    e2.registrar(2, 0)
    assert e2.top(2, 5 * H) == [2, 1]  # empate total: maior id primeiro


def test_curtida_remove_nao_fica_negativa_e_remover_tira_do_ranking():
    e = EmAlta()
    e.registrar(1, 0)
    e.curtida(1, -3)
    assert e.score(1, 0) == 0
    e.remover(1)
    assert e.top(5, 0) == []
    e.curtida(1, +1)  # post que não existe mais: ignora
    assert len(e) == 0


def test_votos_da_historia_valem_para_os_posts_dela():
    e = EmAlta()
    e.registrar(1, 0, historia_id=7)
    e.registrar(2, 0)
    e.voto(7, +4)
    assert e.top(2, 0) == [1, 2]


def test_reconstruir_substitui_o_estado():
    e = EmAlta()
    e.registrar(99, 0)
    e.reconstruir([(1, 0.0, None, 3, 0), (2, 0.0, 5, 0, 0)], {5: 2})
    assert len(e) == 2
    assert e.top(2, 0) == [2, 1] or e.top(2, 0) == [1, 2]
    assert e.score(1, 0) == pontuacao(3, 0, 0, 0)
    assert e.score(2, 0) == pontuacao(0, 0, 2, 0)
