import random
from core.peca import Peca
from typing import Any, Dict, Optional, Sequence
from core.jogador import Jogador

try:

from core.jogador import MCTSJogador, CLIJogador, GAJogador
except ImportError:  # Segurança caso subclasses sejam movidas
    MCTSJogador = CLIJogador = GAJogador = None


def _criar_jogador(nome: str, mao: Sequence[Peca], estrategia: Optional[Any]) -> Jogador:
    """Instancia um ``Jogador`` ou subclasse de acordo com ``estrategia``."""
    if isinstance(estrategia, type) and issubclass(estrategia, Jogador):
        return estrategia(nome, mao)
    return Jogador(nome, mao, estrategia)


def distribuir_jogadores(estrategias: Optional[Dict[str, Any]] = None) -> list[Jogador]:
    """Distribui as peças e cria jogadores com as estratégias informadas."""
    estrategias = estrategias or {}
    todas_pecas = [Peca(i, j) for i in range(7) for j in range(i, 7)]
    random.shuffle(todas_pecas)

    faixas = {
        "J1": (0, 6),
        "J2": (6, 12),
        "J3": (12, 18),
        "J4": (18, 24),
    }

    jogadores = []
    for nome, (i, j) in faixas.items():
        mao = sorted(todas_pecas[i:j], key=lambda p: (p.lado1, p.lado2))
        jogadores.append(_criar_jogador(nome, mao, estrategias.get(nome)))

    return jogadores
