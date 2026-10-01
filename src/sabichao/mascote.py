"""Mascote do Sabichao: uma coruja com capelo em pixel art.

O desenho e gerado por geometria numa grade de 34x32 "pixels" e renderizado com meios-blocos
(half-blocks ▀ ▄): cada caractere do terminal mostra dois pixels, com a cor de cima no texto
e a de baixo no fundo. Os quadros de animacao variam olhos, bico, asas e a borla do capelo.
"""

from __future__ import annotations

import math
from functools import lru_cache

PALETA = {
    ".": None,
    "o": "#3D2B1F",  # contorno
    "B": "#6B4226",  # corpo
    "L": "#8B5E3C",  # brilho corpo
    "C": "#FFF5E6",  # disco facial
    "c": "#F0DCC6",  # disco facial sombra
    "E": "#FFB800",  # iris (amarelo-ambar)
    "K": "#1A1A1A",  # pupilas e boca
    "S": "#FFFFFF",  # reflexo nos olhos
    "b": "#FF6B00",  # bico
    "G": "#1B2A4A",  # capelo
    "g": "#0F1D33",  # capelo contorno
    "T": "#FFD700",  # borla
    "F": "#D4760A",  # pes
    "P": "#FFB6C1",  # bochechas
    "W": "#5C3A1E",  # asa
    "w": "#4A2E17",  # asa ponta
    "V": "#8B6C5C",  # marcas peito (chevrons)
    "Y": "#FFD86B",  # faiscas
    "R": "#C0392B",  # lingua (bico aberto)
}

LARG, ALT = 34, 32
CX, CY = 17, 18

POSES = {
    "normal":      ("abertos",  "fechado", "baixo", "baixo", 0, False),
    "piscando":    ("fechados", "fechado", "baixo", "baixo", 0, False),
    "acenando":    ("abertos",  "fechado", "acima", "baixo", 1, False),
    "acenando2":   ("abertos",  "fechado", "alto",  "baixo", -1, False),
    "comemorando": ("felizes",  "aberto",  "alto",  "alto",  0, True),
    "preocupado":  ("abertos",  "reta",    "baixo", "baixo", 0, False),
}


class _Tela:
    def __init__(self, larg: int = LARG, alt: int = ALT) -> None:
        self.larg, self.alt = larg, alt
        self.px = [["." for _ in range(larg)] for _ in range(alt)]

    def ponto(self, x: int, y: int, cor: str) -> None:
        if 0 <= x < self.larg and 0 <= y < self.alt:
            self.px[y][x] = cor

    def circulo(self, cx: float, cy: float, r: float, cor: str) -> None:
        for y in range(self.alt):
            for x in range(self.larg):
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) < r:
                    self.px[y][x] = cor

    def elipse(self, cx: float, cy: float, rx: float, ry: float, cor: str) -> None:
        for y in range(self.alt):
            for x in range(self.larg):
                dx = (x + 0.5 - cx) / rx
                dy = (y + 0.5 - cy) / ry
                if dx * dx + dy * dy < 1:
                    self.px[y][x] = cor

    def linha(self, x0: int, y0: int, x1: int, y1: int, cor: str) -> None:
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.ponto(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), cor)

    def rect(self, x0: int, y0: int, x1: int, y1: int, cor: str) -> None:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.ponto(x, y, cor)


def _capelo(t: _Tela, borla_dx: int) -> None:
    """Capelo (graduation cap) no topo da cabeca."""
    t.rect(7, 3, 27, 5, "G")
    for x in range(6, 29):
        t.ponto(x, 2, "g")
    for x in range(7, 28):
        t.ponto(x, 6, "g")
    t.ponto(6, 3, "g"); t.ponto(6, 4, "g"); t.ponto(6, 5, "g")
    t.ponto(28, 3, "g"); t.ponto(28, 4, "g"); t.ponto(28, 5, "g")
    for y in range(6, 10):
        margem = (y - 6)
        for x in range(CX - 7 + margem, CX + 7 - margem + 1):
            if t.px[y][x] == ".":
                t.ponto(x, y, "G")
    for x in range(CX - 7, CX + 8):
        if t.px[6][x] == ".":
            t.ponto(x, 6, "g")
    tx = 27 + borla_dx
    t.linha(27, 3, tx, 1, "T")
    t.ponto(tx, 0, "T")
    t.ponto(tx - 1, 0, "T")


def _asa(t: _Tela, lado: int, pose: str) -> None:
    """lado: -1 (esquerda) ou 1 (direita)."""
    x0 = CX + lado * 11
    if pose == "baixo":
        for dy in range(6):
            t.ponto(x0 + lado, CY - 1 + dy, "W")
            t.ponto(x0 + lado * 2, CY + dy, "W")
        t.ponto(x0 + lado * 2, CY + 6, "w")
        t.ponto(x0 + lado * 3, CY + 5, "w")
        t.ponto(x0 + lado * 3, CY + 6, "w")
    elif pose == "acima":
        for dy in range(6):
            t.ponto(x0 + lado, CY - 2 - dy, "W")
            t.ponto(x0 + lado * 2, CY - 3 - dy, "W")
        t.ponto(x0 + lado * 2, CY - 8, "w")
        t.ponto(x0 + lado * 3, CY - 7, "w")
        t.ponto(x0 + lado * 3, CY - 8, "w")
    elif pose == "alto":
        for dy in range(8):
            t.ponto(x0 + lado, CY - 3 - dy, "W")
            t.ponto(x0 + lado * 2, CY - 4 - dy, "W")
        t.ponto(x0 + lado * 2, CY - 11, "w")
        t.ponto(x0 + lado * 3, CY - 10, "w")
        t.ponto(x0 + lado * 3, CY - 11, "w")


@lru_cache(maxsize=None)
def pixels(pose: str = "normal", tamanho: str = "grande") -> tuple[str, ...]:
    if tamanho == "pequeno":
        return _pequeno(pose)
    olhos, bico, esq, dir_, borla_dx, faiscas = POSES[pose]
    t = _Tela()

    _capelo(t, borla_dx)

    t.circulo(CX, CY, 12, "o")
    t.circulo(CX, CY, 11, "B")
    for x, y in ((8, 13), (9, 12), (8, 14), (9, 15)):
        t.ponto(x, y, "L")

    t.elipse(CX, CY - 1.5, 8.5, 7.5, "C")
    t.ponto(CX - 7, CY - 6, "c"); t.ponto(CX + 7, CY - 6, "c")
    t.ponto(CX - 7, CY - 5, "c"); t.ponto(CX + 7, CY - 5, "c")

    for dx in (-8, 8):
        cx = CX + dx
        t.ponto(cx, 8, "o"); t.ponto(cx, 7, "B")
        t.ponto(cx - 1, 8, "o"); t.ponto(cx + 1, 8, "o")
        t.ponto(cx, 9, "B")

    lex, rex = CX - 4, CX + 3
    ey = CY - 4
    if olhos == "abertos":
        for ex in (lex, rex):
            t.circulo(ex + 0.5, ey, 3.6, "o")
            t.circulo(ex + 0.5, ey, 2.8, "E")
            t.circulo(ex + 0.5, ey, 1.5, "K")
            t.ponto(ex - 1, ey - 2, "S"); t.ponto(ex, ey - 2, "S")
    elif olhos == "fechados":
        for ex in (lex, rex):
            for ddx in range(-2, 4):
                t.ponto(ex + ddx, ey, "K")
            t.ponto(ex - 2, ey - 1, "K"); t.ponto(ex + 3, ey - 1, "K")
    elif olhos == "felizes":
        for ex in (lex, rex):
            t.ponto(ex - 1, ey, "K"); t.ponto(ex + 2, ey, "K")
            for ddx in range(0, 3):
                t.ponto(ex + ddx, ey - 1, "K")
                t.ponto(ex - 1 + ddx, ey + 1, ".")

    for dx in (-7, 6):
        t.ponto(CX + dx, CY, "P")
        t.ponto(CX + dx + (1 if dx > 0 else -1), CY, "P")

    bx = CX
    if bico == "fechado":
        t.ponto(bx - 1, CY - 1, "b"); t.ponto(bx, CY - 1, "b"); t.ponto(bx + 1, CY - 1, "b")
        t.ponto(bx, CY, "b")
    elif bico == "aberto":
        t.ponto(bx - 1, CY - 1, "b"); t.ponto(bx, CY - 1, "b"); t.ponto(bx + 1, CY - 1, "b")
        t.ponto(bx - 1, CY, "b"); t.ponto(bx + 1, CY, "b")
        t.ponto(bx, CY, "R")
        t.ponto(bx, CY + 1, "K")
    elif bico == "reta":
        t.ponto(bx - 1, CY - 1, "b"); t.ponto(bx, CY - 1, "b"); t.ponto(bx + 1, CY - 1, "b")
        t.ponto(bx - 1, CY, "b"); t.ponto(bx + 1, CY, "b")

    for vy in (CY + 3, CY + 5, CY + 7):
        for vx in range(-3, 4):
            if abs(vx) == 3:
                t.ponto(CX + vx, vy, "V")
            elif abs(vx) > 0:
                t.ponto(CX + vx, vy, "V")

    _asa(t, -1, esq)
    _asa(t, 1, dir_)

    for px_ in (CX - 5, CX + 3):
        for dx in range(3):
            t.ponto(px_ + dx, CY + 12, "F")
        t.ponto(px_ + 1, CY + 11, "o")

    if faiscas:
        for x, y in ((2, 1), (3, 2), (31, 1), (30, 2), (1, 15), (32, 15)):
            t.ponto(x, y, "Y")

    return tuple("".join(linha) for linha in t.px)


PEQ_LARG, PEQ_ALT = 16, 14


def _pequeno(pose: str) -> tuple[str, ...]:
    olhos, bico, esq, dir_, borla_dx, faiscas = POSES[pose]
    t = _Tela(PEQ_LARG, PEQ_ALT)
    pcx, pcy = 8, 8

    t.rect(3, 0, 12, 1, "G")
    t.ponto(2, 0, "g"); t.ponto(13, 0, "g")
    t.ponto(13 + (1 if borla_dx > 0 else 0), 0, "T")

    t.circulo(pcx, pcy, 5.7, "o")
    t.circulo(pcx, pcy, 4.8, "B")
    t.elipse(pcx, pcy - 0.5, 4, 3.5, "C")
    t.ponto(4, 3, "L"); t.ponto(4, 4, "L")

    for ex in (5, 10):
        if olhos == "abertos":
            t.circulo(ex + 0.5, 6.5, 1.8, "E")
            t.ponto(ex, 6, "K"); t.ponto(ex + 1, 6, "K")
            t.ponto(ex, 7, "K"); t.ponto(ex + 1, 7, "K")
            t.ponto(ex, 6, "S")
        elif olhos == "fechados":
            t.ponto(ex, 7, "K"); t.ponto(ex + 1, 7, "K")
        elif olhos == "felizes":
            t.ponto(ex, 7, "K"); t.ponto(ex + 1, 6, "K")

    t.ponto(pcx, 8, "b")
    if bico == "aberto":
        t.ponto(pcx, 9, "R")

    t.ponto(4, 8, "P"); t.ponto(11, 8, "P")

    for x, pose_asa in ((1, esq), (14, dir_)):
        if pose_asa == "baixo":
            t.ponto(x, 9, "W"); t.ponto(x, 10, "w")
        elif pose_asa == "acima":
            t.ponto(x, 6, "W"); t.ponto(x, 5, "w")
        else:
            t.ponto(x, 5, "W"); t.ponto(x, 4, "W"); t.ponto(x, 3, "w")

    for x in (6, 10):
        t.ponto(x, 13, "F")

    if faiscas:
        for x, y in ((0, 0), (15, 0), (0, 12), (15, 12)):
            t.ponto(x, y, "Y")

    return tuple("".join(linha) for linha in t.px)


def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def render(pose: str = "normal", tamanho: str = "grande") -> str:
    """Renderiza o mascote como string com cores ANSI 24-bit (meios-blocos)."""
    px = list(pixels(pose, tamanho))
    largura = len(px[0])
    if len(px) % 2:
        px.append("." * largura)
    partes: list[str] = []
    for y in range(0, len(px), 2):
        for x in range(largura):
            cima = PALETA[px[y][x]]
            baixo = PALETA[px[y + 1][x]]
            if cima is None and baixo is None:
                partes.append(" ")
            elif cima is None:
                r, g, b_ = _hex_rgb(baixo)
                partes.append(f"\033[38;2;{r};{g};{b_}m▄\033[0m")
            elif baixo is None:
                r, g, b_ = _hex_rgb(cima)
                partes.append(f"\033[38;2;{r};{g};{b_}m▀\033[0m")
            else:
                r1, g1, b1 = _hex_rgb(cima)
                r2, g2, b2 = _hex_rgb(baixo)
                partes.append(f"\033[38;2;{r1};{g1};{b1};48;2;{r2};{g2};{b2}m▀\033[0m")
        if y + 2 < len(px):
            partes.append("\n")
    return "".join(partes)


ANIMACOES: dict[str, list[tuple[str, float]]] = {
    "ocioso":      [("normal", 3.2), ("piscando", 0.18), ("normal", 2.4), ("piscando", 0.15),
                    ("normal", 0.2), ("piscando", 0.15)],
    "acenando":    [("acenando", 0.35), ("acenando2", 0.35)] * 3 + [("normal", 1.0)],
    "comemorando": [("comemorando", 0.5), ("acenando2", 0.3)],
    "preocupado":  [("preocupado", 2.5), ("piscando", 0.15)],
}
