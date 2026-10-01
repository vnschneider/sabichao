"""Gera os SVGs do mascote e copia os scripts de instalacao para o site.

Uso: uv run python site/gerar_mascote.py
"""

import shutil
from pathlib import Path

# O import funciona a partir da raiz do projeto (uv run).
from sabichao import mascote

DESTINO = Path(__file__).parent / "public"


def svg(pose: str, tamanho: str = "grande") -> str:
    px = mascote.pixels(pose, tamanho)
    larg, alt = len(px[0]), len(px)
    rects = [f'<rect x="{x}" y="{y}" width="1" height="1" fill="{mascote.PALETA[c]}"/>'
             for y, linha in enumerate(px) for x, c in enumerate(linha) if mascote.PALETA[c]]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {larg} {alt}" shape-rendering="crispEdges" '
            f'role="img" aria-label="Mascote do Sabichao: uma coruja com capelo">{"".join(rects)}</svg>\n')


if __name__ == "__main__":
    for pose in ("acenando", "comemorando", "normal", "piscando"):
        (DESTINO / f"mascote-{pose}.svg").write_text(svg(pose), encoding="utf-8")
    (DESTINO / "favicon.svg").write_text(svg("normal", "pequeno"), encoding="utf-8")

    raiz = Path(__file__).parent.parent
    for script in ("install.ps1", "install.sh"):
        shutil.copy2(raiz / script, DESTINO / script)

    print("SVGs e scripts gerados em", DESTINO)
