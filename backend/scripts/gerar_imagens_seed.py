"""Gera as ilustrações SVG do seed em frontend/public/seed/ (versionadas no repo).

As imagens ficam no `public/` do front, não no `uploads/` (que some no deploy).
Rode só se quiser regerar: uv run python scripts/gerar_imagens_seed.py
"""

from pathlib import Path

DESTINO = Path(__file__).resolve().parents[2] / "frontend" / "public" / "seed"


def _svg(fundo: tuple[str, str], corpo: str) -> str:
    a, b = fundo
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 400">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/>'
        f"</linearGradient></defs>"
        f'<rect width="640" height="400" fill="url(#g)"/>{corpo}</svg>'
    )


def _estrelas(n: int, cor: str = "#fff") -> str:
    return "".join(
        f'<circle cx="{(i * 97) % 640}" cy="{(i * 53) % 220}" r="{1 + i % 3}" fill="{cor}" opacity=".8"/>'
        for i in range(n)
    )


IMAGENS = {
    "fantasia-torre": _svg(("#2b1b5a", "#e08a6b"), _estrelas(25)
        + '<circle cx="500" cy="90" r="40" fill="#ffe9a8"/>'
        '<path d="M0 400V320Q160 260 320 330T640 300V400Z" fill="#1c1238"/>'
        '<rect x="290" y="130" width="60" height="200" fill="#100a24"/>'
        '<path d="M280 130L320 60L360 130Z" fill="#100a24"/>'
        '<rect x="312" y="160" width="16" height="28" fill="#ffd25e"/>'),
    "fantasia-dragao": _svg(("#12363a", "#7ac7a0"), _estrelas(12)
        + '<path d="M0 400V300L120 220L240 300L380 190L520 300L640 240V400Z" fill="#0b2325"/>'
        '<path d="M200 150Q320 60 440 150Q380 130 320 170Q260 130 200 150Z" fill="#c2412d"/>'
        '<circle cx="320" cy="150" r="14" fill="#c2412d"/>'),
    "fantasia-floresta": _svg(("#1e3a24", "#a9d36b"),
        "".join(f'<path d="M{x} 400L{x+40} 200L{x+80} 400Z" fill="#0f2414" opacity=".{6+i%3}"/>'
                for i, x in enumerate(range(-20, 640, 70)))
        + '<circle cx="320" cy="260" r="22" fill="#fff6b0" opacity=".9"/>'),
    "terror-casa": _svg(("#1a0f1f", "#4a1d2e"), _estrelas(15, "#d9d0e0")
        + '<circle cx="120" cy="80" r="44" fill="#e9e4d4"/>'
        '<rect x="200" y="190" width="240" height="160" fill="#08050b"/>'
        '<path d="M180 190L320 100L460 190Z" fill="#08050b"/>'
        '<rect x="300" y="250" width="40" height="100" fill="#3a0f14"/>'
        '<rect x="226" y="220" width="30" height="36" fill="#d4a017"/>'
        '<rect x="384" y="220" width="30" height="36" fill="#d4a017"/>'),
    "terror-olhos": _svg(("#050505", "#1f0a0a"),
        "".join(f'<ellipse cx="{x}" cy="{y}" rx="16" ry="9" fill="#e8d8c0"/>'
                f'<circle cx="{x}" cy="{y}" r="5" fill="#b00020"/>'
                for x, y in [(120, 90), (300, 200), (480, 120), (540, 290), (180, 310)])),
    "terror-corredor": _svg(("#0c0c14", "#2a2438"),
        '<path d="M0 0L240 120V280L0 400Z" fill="#14121c"/>'
        '<path d="M640 0L400 120V280L640 400Z" fill="#14121c"/>'
        '<rect x="240" y="120" width="160" height="160" fill="#05050a"/>'
        '<rect x="300" y="170" width="40" height="110" fill="#6d0f1d"/>'),
    "sol-cafe": _svg(("#fde8c9", "#f4b183"),
        '<rect x="200" y="200" width="240" height="30" rx="8" fill="#8a5a44"/>'
        '<path d="M240 120h160v80q0 40-80 40t-80-40Z" fill="#fff"/>'
        '<path d="M400 140q50 0 50 40t-50 40" fill="none" stroke="#fff" stroke-width="12"/>'
        '<path d="M290 90q-10-20 0-40M330 90q-10-20 0-40M370 90q-10-20 0-40" stroke="#c98c6a" stroke-width="6" fill="none"/>'),
    "sol-janela": _svg(("#bfe3f2", "#f6e7cb"),
        '<rect x="170" y="60" width="300" height="280" fill="#fff" stroke="#6b4f3a" stroke-width="14"/>'
        '<path d="M320 60V340M170 200H470" stroke="#6b4f3a" stroke-width="10"/>'
        '<ellipse cx="260" cy="130" rx="40" ry="16" fill="#fff"/>'
        '<rect x="0" y="340" width="640" height="60" fill="#c9a37e"/>'
        '<rect x="400" y="300" width="40" height="40" fill="#5a8f4a"/>'),
    "sol-onibus": _svg(("#f7c6a3", "#f48c8c"),
        '<rect x="0" y="300" width="640" height="100" fill="#4a4a5a"/>'
        '<rect x="120" y="190" width="400" height="120" rx="20" fill="#ffd25e"/>'
        + "".join(f'<rect x="{150 + i*90}" y="210" width="60" height="50" fill="#bfe3f2"/>' for i in range(4))
        + '<circle cx="200" cy="315" r="26" fill="#222"/><circle cx="440" cy="315" r="26" fill="#222"/>'),
    "scifi-estacao": _svg(("#050a1f", "#1b2a5e"), _estrelas(40)
        + '<ellipse cx="320" cy="210" rx="190" ry="36" fill="none" stroke="#6fd3ff" stroke-width="8"/>'
        '<circle cx="320" cy="210" r="46" fill="#2c3e7a"/>'
        '<circle cx="320" cy="210" r="18" fill="#6fd3ff"/>'),
    "scifi-planeta": _svg(("#0b0420", "#3a1a5e"), _estrelas(35)
        + '<circle cx="320" cy="260" r="150" fill="#d1693b"/>'
        '<path d="M190 240Q320 280 450 230" stroke="#f0a070" stroke-width="14" fill="none"/>'
        '<path d="M200 300Q320 340 440 290" stroke="#a84a24" stroke-width="10" fill="none"/>'),
    "scifi-robo": _svg(("#102a43", "#486581"),
        '<rect x="250" y="110" width="140" height="110" rx="18" fill="#bcccdc"/>'
        '<circle cx="290" cy="165" r="16" fill="#102a43"/><circle cx="350" cy="165" r="16" fill="#00e5ff"/>'
        '<rect x="270" y="225" width="100" height="110" rx="10" fill="#9fb3c8"/>'
        '<path d="M320 110V70" stroke="#bcccdc" stroke-width="8"/><circle cx="320" cy="62" r="10" fill="#ff6b6b"/>'),
}


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, svg in IMAGENS.items():
        (DESTINO / f"{nome}.svg").write_text(svg, encoding="utf-8")
    print(f"{len(IMAGENS)} imagens em {DESTINO}")


if __name__ == "__main__":
    main()
