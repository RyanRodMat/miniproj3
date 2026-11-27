"""Árvore da história: capítulos são nós, as opções de cada decisão são as arestas.

Python puro: nenhum import de SQLAlchemy/FastAPI. A API alimenta a estrutura
com ints, strings e listas.

    cap 1 ──(opção 0, vencedora)──> cap 2 ──(opção 1, vencedora)──> cap 3
       └─ opção 1 (não escolhida: "o que poderia ter sido")

Custos (n = capítulos, k = opções por decisão, no máximo 4, d = profundidade):
- adicionar_capitulo / abrir_decisao / vencedora / encerrada: O(1) (hash)
- encerrar (fecha a votação e calcula a vencedora):           O(k) = O(1)
- caminho (percorrer o que foi escolhido):                    O(d)
- reconstruir (só no startup):                                O(n)
"""

from dataclasses import dataclass, field


@dataclass
class No:
    capitulo_id: int
    historia_id: int
    pai_id: int | None
    opcao_origem: int | None  # qual opção do pai levou até aqui
    opcoes: list[str] = field(default_factory=list)  # vazio = capítulo sem decisão
    votos_finais: list[int] | None = None  # preenchido ao encerrar
    filhos: dict[int, int] = field(default_factory=dict)  # opção -> capitulo_id

    @property
    def tem_decisao(self) -> bool:
        return bool(self.opcoes)

    @property
    def encerrada(self) -> bool:
        return self.votos_finais is not None

    @property
    def vencedora(self) -> int | None:
        """Opção mais votada; empate vai para a de menor índice; sem votos, None."""
        if self.votos_finais is None or sum(self.votos_finais) == 0:
            return None
        return max(range(len(self.votos_finais)), key=lambda i: (self.votos_finais[i], -i))


class Jornada:
    def __init__(self) -> None:
        self._nos: dict[int, No] = {}
        self._raiz: dict[int, int] = {}  # historia_id -> capitulo_id do primeiro capítulo

    def reconstruir(
        self,
        capitulos: list[tuple[int, int, int | None, int | None]],
        decisoes: list[tuple[int, list[str], list[int] | None]],
    ) -> None:
        """Startup. capitulos: (id, historia_id, pai_id, opcao_origem), pais antes dos
        filhos. decisoes: (capitulo_id, opcoes, votos_finais ou None se a votação segue aberta)."""
        self._nos = {}
        self._raiz = {}
        for cap_id, historia_id, pai_id, opcao in capitulos:
            self.adicionar_capitulo(cap_id, historia_id, pai_id, opcao)
        for cap_id, opcoes, votos in decisoes:
            self.abrir_decisao(cap_id, opcoes)
            if votos is not None:
                self.encerrar(cap_id, votos)

    def adicionar_capitulo(
        self, capitulo_id: int, historia_id: int, pai_id: int | None, opcao_origem: int | None
    ) -> None:
        """Publicou um capítulo. O(1)."""
        self._nos[capitulo_id] = No(capitulo_id, historia_id, pai_id, opcao_origem)
        if pai_id is None:
            self._raiz[historia_id] = capitulo_id
        else:
            self._nos[pai_id].filhos[opcao_origem] = capitulo_id

    def abrir_decisao(self, capitulo_id: int, opcoes: list[str]) -> None:
        """O capítulo terminou numa decisão. O(1)."""
        self._nos[capitulo_id].opcoes = list(opcoes)

    def encerrar(self, capitulo_id: int, votos: list[int]) -> None:
        """A votação acabou: congela os votos e, com eles, a opção vencedora. O(k)."""
        self._nos[capitulo_id].votos_finais = list(votos)

    def no(self, capitulo_id: int) -> No | None:
        return self._nos.get(capitulo_id)

    def encerrada(self, capitulo_id: int) -> bool:
        no = self._nos.get(capitulo_id)
        return no is not None and no.encerrada

    def vencedora(self, capitulo_id: int) -> int | None:
        no = self._nos.get(capitulo_id)
        return no.vencedora if no else None

    def caminho(self, historia_id: int) -> list[No]:
        """Capítulos na ordem em que a história realmente seguiu: da raiz, sempre pelo
        filho da opção vencedora. Para onde não há decisão encerrada ou filho publicado.
        O(d)."""
        atual = self._raiz.get(historia_id)
        percorrido: list[No] = []
        while atual is not None:
            no = self._nos[atual]
            percorrido.append(no)
            vencedora = no.vencedora
            atual = no.filhos.get(vencedora) if vencedora is not None else None
        return percorrido


# O singleton que a API importa (ver app/services/decisoes.py e o lifespan em main.py).
jornada = Jornada()
