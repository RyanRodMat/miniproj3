"""Ranking "Em alta": engajamento recente de cada post, com heap top-K.

Python puro: nenhum import de SQLAlchemy/FastAPI. A API alimenta a estrutura com
ids, contagens e timestamps (segundos desde a época).

    score = (curtidas + 2·comentários + 3·votos) / (horas_desde_criação + 2) ** 1.5

O denominador cresce com o tempo, então um post antigo precisa de muito mais
engajamento para continuar no topo: quem engaja *agora* sobe, quem já é famoso
não fica lá para sempre. Como o score muda com o relógio, não dá para guardar um
heap pronto; o que fica em memória são os contadores (atualizados em O(1) a cada
write) e o heap é montado na consulta com `heapq.nlargest`.

- curtir / comentar / votar / criar / apagar: O(1) (dict)
- top-K entre n posts: O(n log K), em vez de O(n log n) ordenando tudo
- reconstruir do zero: O(n), só no startup
"""

import heapq
from dataclasses import dataclass

PESO_CURTIDA = 1
PESO_COMENTARIO = 2
PESO_VOTO = 3
EXPOENTE = 1.5
SUAVIZACAO_HORAS = 2  # evita divisão por ~0 e o salto absurdo de um post de 1 minuto


@dataclass
class _Post:
    criado_em: float
    historia_id: int | None = None
    curtidas: int = 0
    comentarios: int = 0


def pontuacao(curtidas: int, comentarios: int, votos: int, horas: float) -> float:
    """Score de um post. `horas` negativas (relógio torto) contam como 0."""
    engajamento = (
        PESO_CURTIDA * curtidas + PESO_COMENTARIO * comentarios + PESO_VOTO * votos
    )
    return engajamento / (max(horas, 0.0) + SUAVIZACAO_HORAS) ** EXPOENTE


class EmAlta:
    def __init__(self) -> None:
        self._posts: dict[int, _Post] = {}
        # votos de uma história valem para os posts dela (posts de "novo capítulo")
        self._votos_da_historia: dict[int, int] = {}

    def reconstruir(
        self,
        posts: list[tuple[int, float, int | None, int, int]],
        votos_por_historia: dict[int, int],
    ) -> None:
        """Startup: (post_id, criado_em, historia_id, curtidas, comentarios) de cada post."""
        self._posts = {
            pid: _Post(criado, hid, curtidas, comentarios)
            for pid, criado, hid, curtidas, comentarios in posts
        }
        self._votos_da_historia = dict(votos_por_historia)

    def registrar(self, post_id: int, criado_em: float, historia_id: int | None = None) -> None:
        self._posts[post_id] = _Post(criado_em, historia_id)

    def remover(self, post_id: int) -> None:
        self._posts.pop(post_id, None)

    def curtida(self, post_id: int, delta: int) -> None:
        p = self._posts.get(post_id)
        if p:
            p.curtidas = max(0, p.curtidas + delta)

    def comentario(self, post_id: int, delta: int) -> None:
        p = self._posts.get(post_id)
        if p:
            p.comentarios = max(0, p.comentarios + delta)

    def voto(self, historia_id: int, delta: int = 1) -> None:
        total = max(0, self._votos_da_historia.get(historia_id, 0) + delta)
        self._votos_da_historia[historia_id] = total

    def __len__(self) -> int:
        return len(self._posts)

    def score(self, post_id: int, agora: float) -> float:
        p = self._posts[post_id]
        votos = self._votos_da_historia.get(p.historia_id, 0) if p.historia_id else 0
        return pontuacao(p.curtidas, p.comentarios, votos, (agora - p.criado_em) / 3600)

    def top(self, k: int, agora: float) -> list[int]:
        """Ids dos k posts mais quentes. Empate de score: mais novo primeiro (depois, maior id)."""
        if k <= 0:
            return []
        return heapq.nlargest(
            k,
            self._posts,
            key=lambda pid: (self.score(pid, agora), self._posts[pid].criado_em, pid),
        )


# O singleton que a API importa (ver services/em_alta.py e o lifespan em main.py).
em_alta = EmAlta()
