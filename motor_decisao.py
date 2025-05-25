# motor_decisao.py

import random
from collections import deque
from motor_de_jogo_com_motor_decisao import gerar_pecas, jogar_peca, jogadas_validas, proximo_jogador, calcular_pontuacao_batida, calcular_pontuacao_travamento, tipo_de_batida, continuar_rodada

def escolher_peca_mcts(jogador, mao, jogadas, tabuleiro, pontas, historico, n_simulacoes=20):
    resultados = {}
    for peca in jogadas:
        vitorias = 0
        for _ in range(n_simulacoes):
            vitoria = simular_partida_com_jogada_inicial(
                jogador, mao, peca, tabuleiro, pontas, historico
            )
            if vitoria:
                vitorias += 1
        resultados[peca] = vitorias / n_simulacoes

    return max(resultados, key=resultados.get)

def simular_partida_com_jogada_inicial(jogador, mao_original, peca_escolhida, tabuleiro, pontas, historico):
    maos, _ = gerar_maos_ocultas(jogador, mao_original, historico, peca_escolhida)
    tabuleiro_sim = deque(tabuleiro)
    pontas_sim = pontas[:]

    # Joga a peca inicial
    maos[jogador].remove(peca_escolhida)
    jogar_peca(tabuleiro_sim, pontas_sim, peca_escolhida)

    proximo = proximo_jogador(jogador)
    resultado = continuar_rodada(maos, tabuleiro_sim, pontas_sim, proximo)

    dupla_jogador = ["J1", "J3"] if jogador in ["J1", "J3"] else ["J2", "J4"]
    return resultado["final"]["vencedor_rodada"] in dupla_jogador

def gerar_maos_ocultas(jogador, mao_jogador, historico, peca_inicial):
    todas_pecas = gerar_pecas()
    usadas = set([peca_inicial])

    for evento in historico:
        if "peca" in evento:
            usadas.add(evento["peca"])

    usadas.update(mao_jogador)
    restantes = [p for p in todas_pecas if p not in usadas]
    random.shuffle(restantes)

    maos = {j: [] for j in ["J1", "J2", "J3", "J4"]}
    maos[jogador] = mao_jogador[:]

    outros = [j for j in maos if j != jogador]
    for j in outros:
        maos[j] = sorted(restantes[:6])
        restantes = restantes[6:]

    return maos, restantes
