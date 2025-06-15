"""motor_ga_patch.py - adaptador para o algoritmo genético

Este módulo expõe as funções ``run_match_v2`` e ``simulate_round_v2`` de
forma compatível com o GA descrito em ``ga_domino.py``. Elas utilizam o
motor definido em ``motor_de_jogo.py``.

Os pesos recebidos são aplicados aos jogadores J1 e J3, permitindo avaliar heurísticas baseadas nesses valores.
"""
from __future__ import annotations

import random
from typing import List

from motor_de_jogo import simular_rodada, simular_partida
from utilidades.distribuicao import distribuir_jogadores
from core.jogador import escolher_peca_ga


def simulate_round_v2(_pesos: List[float]) -> int:
    """Executa uma única rodada e devolve o índice do jogador vencedor.

    Caso a rodada termine empatada (travamento), ``-1`` é retornado.
    Os pesos são aplicados às jogadas de ``J1`` e ``J3``.
    """
    estrategia_ga = lambda j, t, js: escolher_peca_ga(j, t, js, _pesos)
    estrategias = {"J1": estrategia_ga, "J3": estrategia_ga}
    jogadores = distribuir_jogadores(estrategias)
    resultado = simular_rodada(jogadores)
    vencedor = resultado["final"]["vencedor_rodada"]
    nomes = ["J1", "J2", "J3", "J4"]
    return nomes.index(vencedor) if vencedor in nomes else -1


def run_match_v2(_pesos: List[float], n_games: int = 120) -> int:
    """Retorna quantas partidas foram vencidas pela ``Dupla_1``.

    Os pesos são aplicados às jogadas de ``J1`` e ``J3``.
    """
    estrategia_ga = lambda j, t, js: escolher_peca_ga(j, t, js, _pesos)
    estrategias = {"J1": estrategia_ga, "J3": estrategia_ga}
    vitorias = 0
    for _ in range(n_games):
        resultado = simular_partida(estrategias=estrategias)
        if resultado["vencedor_partida"] == "Dupla_1":
            vitorias += 1
    return vitorias


if __name__ == "__main__":
    random_pesos = [random.uniform(-5, 5) for _ in range(8)]
    print("Vitórias da Dupla 1 em 10 partidas:", run_match_v2(random_pesos, 10))
