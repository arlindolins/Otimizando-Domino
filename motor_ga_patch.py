"""motor_ga_patch.py — Integra GA ao seu simulador

Coloque este arquivo na mesma pasta de *motor_de_jogo.py*.
Ele fornece:
    • run_match_v2(weights, n_games)
    • simulate_round_v2(weights)  (adapta o loop já existente)

Só depende dos módulos que você já enviou: peca, jogador, tabuleiro, etc.
Copie/cole ou importe conforme organização do seu projeto.
"""
from __future__ import annotations
import random
from typing import List

from core.peca import Peca
from core.jogador import Jogador
from core.tabuleiro import Tabuleiro
from jogo.rodada import Rodada
from jogo.partida import Partida

################################################################################
# 1.  Estratégia da Dupla 1 parametrizada pelos 8 pesos                       #
################################################################################

def estrategia_dupla1(jogador: Jogador, tabuleiro: Tabuleiro, pesos: List[float],
                      lacks, placar_duplas) -> tuple[Peca, str|None]:
    """Retorna (peça escolhida, lado ['esquerda'|'direita'|None])
    lado None significa primeira peça da rodada.
    """
    w0, w1, w2, w3, w4, w5, w6, w7 = pesos
    mao = jogador.mao
    left, right = tabuleiro.obter_pontas()

    # Construir listas de movimentos válidos -------------------------------
    movimentos = []  # (peca, lado, score)

    def pode_colocar(piece: Peca, lado: str|None):
        if lado is None:
            return True
        return piece.encaixa(left if lado == "esquerda" else right)

    for p in mao:
        if left is None:  # primeira jogada da rodada
            movimentos.append((p, None))
        else:
            if pode_colocar(p, "esquerda"):
                movimentos.append((p, "esquerda"))
            if pode_colocar(p, "direita"):
                movimentos.append((p, "direita"))

    if not movimentos:
        return None, None

    # Dados auxiliares ------------------------------------------------------
    parceiro = (jogador.posicao + 2) % 4
    oponentes = [(jogador.posicao + 1) % 4, (jogador.posicao + 3) % 4]

    def can_play(player_idx: int, L: int, R: int):
        return not (L in lacks[player_idx] and R in lacks[player_idx])

    # Avaliar score de cada movimento --------------------------------------
    melhor, melhor_score = movimentos[0], -1e9
    for peca, lado in movimentos:
        if left is None:  # abertura -> mantém escolha de maior duplo
            if peca.is_duplo():
                return peca, None
            continue
        # Simular novas pontas
        L, R = tabuleiro.projetar_pontas(peca, lado)
        opp_can       = sum(can_play(o, L, R) for o in oponentes)
        partner_can   = 1 if can_play(parceiro, L, R) else 0
        # unknown counts (simplificado): assume peças restantes igualmente prováveis
        opp_unknown   = 0
        partner_unknown = 0
        own_future    = sum(1 for q in mao if q != peca and q.encaixa(L) or q.encaixa(R))
        pip_sum       = peca.lado1 + peca.lado2
        # Tipo de batida possível
        if jogador.pode_bater_com(peca, L, R):
            can_finish_type = jogador.tipo_batida_no_lance(peca, L, R)
        else:
            can_finish_type = 0
        enemy_close_to_game = 1 if max(placar_duplas) >= 5 else 0

        score = (
            w0 * (-opp_can) + w1 * partner_can +
            w2 * (-opp_unknown) + w3 * partner_unknown +
            w4 * own_future + w5 * pip_sum +
            w6 * can_finish_type + w7 * enemy_close_to_game
        )
        if score > melhor_score:
            melhor_score, melhor = (peca, lado)
    return melhor

################################################################################
# 2.  Simular UMA rodada com pesos                                            #
################################################################################

def simulate_round_v2(pesos: List[float]):
    """Simula uma rodada única.  Retorna o índice do jogador vencedor (0..3)."""
    partida = Partida(jogadores=[f"J{i+1}" for i in range(4)])
    rodada = Rodada(partida)

    # Distribuição inicial já está em Rodada.__init__
    lacks = [set() for _ in range(4)]

    while True:
        jogador_atual = rodada.jogador_atual
        if jogador_atual.posicao in (0, 2):  # Dupla 1 usa pesos
            peca, lado = estrategia_dupla1(jogador_atual, rodada.tabuleiro,
                                           pesos, lacks, partida.placar_duplas)
        else:  # Dupla 2 – baseline
            peca, lado = jogador_atual.estrategia_baseline(rodada.tabuleiro)

        if peca is None:  # passa
            left, right = rodada.tabuleiro.obter_pontas()
            lacks[jogador_atual.posicao].update([left, right])
            rodada.registrar_passe()
        else:
            rodada.jogar(jogador_atual, peca, lado)
            # limpar lacks – sabemos que esse jogador tem agora essas pontas
            # já não faz falta explicita

        if rodada.concluida:
            return rodada.vencedor.posicao

################################################################################
# 3.  n partidas + pontos até fechar partida (6 pts)                          #
################################################################################

def run_match_v2(pesos: List[float], n_games: int = 120) -> int:
    """Retorna vitórias da Dupla 1 em n_games partidas completas."""
    vitorias = 0
    for _ in range(n_games):
        placar_duplas = [0, 0]
        while max(placar_duplas) < 6:
            ganhador_rodada = simulate_round_v2(pesos)
            dupla = 0 if ganhador_rodada in (0, 2) else 1
            # 1 ponto por rodada (simplificação).  Use lógica detalhada se quiser.
            placar_duplas[dupla] += 1
        if placar_duplas[0] > placar_duplas[1]:
            vitorias += 1
    return vitorias

################################################################################
# 4.  Teste rápido                                                            #
################################################################################
if __name__ == "__main__":
    random_pesos = [random.uniform(-5, 5) for _ in range(8)]
    print("Vitórias da Dupla 1 em 10 partidas:", run_match_v2(random_pesos, 10))
