"""mcts_engine.py - Motor de decisão MCTS

Este módulo oferece a função ``escolher_peca_mcts`` utilizada pelo
``motor_de_jogo`` para determinar a jogada dos jogadores da Dupla 1.
"""

from __future__ import annotations

import random
from collections import deque
from typing import List

from core.jogador import Jogador
from core.peca import Peca
from core.tabuleiro import Tabuleiro
from regras.game_logic import proximo_jogador_obj, determinar_vencedor_travamento

SIMULACOES_PADRAO = 30


def _copiar_estado(jogadores: List[Jogador], tabuleiro: Tabuleiro) -> tuple[List[Jogador], Tabuleiro]:
    """Cria cópias superficiais do estado atual do jogo."""
    jogadores_copia = [Jogador(j.nome, j.mao.copy()) for j in jogadores]
    tab_copia = Tabuleiro()
    tab_copia.pecas = deque(tabuleiro.pecas)
    tab_copia.pontas = tabuleiro.pontas.copy()
    return jogadores_copia, tab_copia


def _simular_jogo_random(jogadores: List[Jogador], jogador_atual: Jogador, tabuleiro: Tabuleiro) -> str:
    """Executa jogadas aleatórias até o término da rodada e retorna o vencedor."""
    passes = 0
    while True:
        jogadas = jogador_atual.jogadas_validas(tabuleiro.obter_pontas())
        if jogadas:
            p = random.choice(jogadas)
            jogador_atual.remover_peca(p)
            tabuleiro.jogar(p)
            passes = 0
            if not jogador_atual.mao:
                return jogador_atual.nome
        else:
            passes += 1
            if passes == 4:
                vencedor, _ = determinar_vencedor_travamento(jogadores)
                return vencedor or ""
        jogador_atual = proximo_jogador_obj(jogadores, jogador_atual)


def escolher_peca_mcts(jogador: Jogador, jogadores: List[Jogador], tabuleiro: Tabuleiro, simulations: int = SIMULACOES_PADRAO) -> Peca:
    """Seleciona a peça mais promissora para ``jogador`` via simulações Monte Carlo."""
    jogadas = jogador.jogadas_validas(tabuleiro.obter_pontas())
    if not jogadas:
        raise ValueError("Jogador não possui jogadas válidas")

    melhor_peca = jogadas[0]
    melhor_taxa = -1.0

    for peca in jogadas:
        vitorias = 0
        for _ in range(simulations):
            jogadores_copia, tab_copia = _copiar_estado(jogadores, tabuleiro)
            j_copia = next(j for j in jogadores_copia if j.nome == jogador.nome)
            j_copia.remover_peca(peca)
            tab_copia.jogar(peca)
            if not j_copia.mao:
                vitorias += 1
            else:
                proximo = proximo_jogador_obj(jogadores_copia, j_copia)
                vencedor = _simular_jogo_random(jogadores_copia, proximo, tab_copia)
                if vencedor == jogador.nome:
                    vitorias += 1
        taxa = vitorias / simulations
        if taxa > melhor_taxa:
            melhor_taxa = taxa
            melhor_peca = peca

    return melhor_peca


if __name__ == "__main__":
    print("Este módulo fornece apenas a função de decisão e não deve ser executado diretamente.")
