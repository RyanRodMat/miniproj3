"""core/jornada.py em Python puro: sem servidor, sem banco."""

from app.core.jornada import Jornada


def _historia() -> Jornada:
    j = Jornada()
    j.adicionar_capitulo(1, 10, None, None)
    j.abrir_decisao(1, ["luta", "foge", "negocia"])
    return j


def test_caminho_segue_a_opcao_vencedora():
    j = _historia()
    j.encerrar(1, [1, 5, 2])  # "foge" vence
    j.adicionar_capitulo(2, 10, 1, 1)
    assert [n.capitulo_id for n in j.caminho(10)] == [1, 2]
    # os outros ramos não têm capítulo: ficam só como opções não escolhidas
    assert j.no(1).filhos == {1: 2}


def test_caminho_para_enquanto_a_votacao_esta_aberta():
    j = _historia()
    assert [n.capitulo_id for n in j.caminho(10)] == [1]
    assert j.vencedora(1) is None and not j.encerrada(1)


def test_empate_vence_o_menor_indice_e_sem_votos_nao_ha_vencedora():
    j = _historia()
    j.encerrar(1, [0, 3, 3])
    assert j.vencedora(1) == 1

    j2 = _historia()
    j2.encerrar(1, [0, 0, 0])
    assert j2.encerrada(1) and j2.vencedora(1) is None


def test_historias_sao_independentes_e_inexistente_e_vazia():
    j = _historia()
    j.adicionar_capitulo(7, 20, None, None)
    assert [n.capitulo_id for n in j.caminho(20)] == [7]
    assert j.caminho(999) == []


def test_reconstruir_reproduz_a_mesma_arvore():
    j = _historia()
    j.encerrar(1, [0, 4, 1])
    j.adicionar_capitulo(2, 10, 1, 1)
    j.abrir_decisao(2, ["a", "b"])

    novo = Jornada()
    novo.reconstruir(
        [(1, 10, None, None), (2, 10, 1, 1)],
        [(1, ["luta", "foge", "negocia"], [0, 4, 1]), (2, ["a", "b"], None)],
    )
    assert [n.capitulo_id for n in novo.caminho(10)] == [1, 2]
    assert novo.vencedora(1) == 1 and not novo.encerrada(2)
