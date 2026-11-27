"""make bench: heap top-K (heapq.nlargest) vs. ordenar tudo, no ranking Em alta."""

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.em_alta import EmAlta

K = 20  # uma página do Em alta
AGORA = 1_000_000 * 3600.0


def montar(n: int) -> EmAlta:
    rnd = random.Random(7)
    e = EmAlta()
    for pid in range(n):
        e.registrar(pid, AGORA - rnd.random() * 720 * 3600)
        e.curtida(pid, rnd.randint(0, 50))
        e.comentario(pid, rnd.randint(0, 10))
    return e


def medir(f, vezes: int = 5) -> float:
    melhor = float("inf")
    for _ in range(vezes):
        t = time.perf_counter()
        f()
        melhor = min(melhor, time.perf_counter() - t)
    return melhor * 1000


def ordenar_tudo(e: EmAlta, k: int) -> list[int]:
    ids = sorted(
        e._posts, key=lambda p: (e.score(p, AGORA), e._posts[p].criado_em, p), reverse=True
    )
    return ids[:k]


if __name__ == "__main__":
    print(f"top-{K} do Em alta: heap (nlargest) vs. sorted — melhor de 5, em ms")
    print(f"{'posts':>10} {'heap':>10} {'sorted':>10}")
    for n in (1_000, 10_000, 100_000):
        e = montar(n)
        assert e.top(K, AGORA) == ordenar_tudo(e, K)
        print(f"{n:>10} {medir(lambda: e.top(K, AGORA)):>10.2f} {medir(lambda: ordenar_tudo(e, K)):>10.2f}")
