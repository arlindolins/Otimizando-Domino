import random
from core.peca import Peca
from core.jogador import Jogador

def distribuir_jogadores() -> list[Jogador]:
    todas_pecas = [Peca(i, j) for i in range(7) for j in range(i, 7)]
    random.shuffle(todas_pecas)
    return [
        Jogador("J1", sorted(todas_pecas[0:6], key=lambda p: (p.lado1, p.lado2))),
        Jogador("J2", sorted(todas_pecas[6:12], key=lambda p: (p.lado1, p.lado2))),
        Jogador("J3", sorted(todas_pecas[12:18], key=lambda p: (p.lado1, p.lado2))),
        Jogador("J4", sorted(todas_pecas[18:24], key=lambda p: (p.lado1, p.lado2)))
    ]
