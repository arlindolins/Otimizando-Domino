# main.py

from motor_decisao import escolher_peca_mcts
from collections import deque
import copy
import random

def simular_rodada_com_dupla_mcts():
    maos, _ = distribuir_pecas()
    jogador, maior_duplo = max(
        ((j, p[0]) for j, m in maos.items() for p in m if p[0] == p[1]),
        key=lambda x: x[1],
        default=(None, -1)
    )

    if jogador is None:
        return {"erro": "Nenhum duplo encontrado"}

    tabuleiro = deque()
    pontas = [None, None]
    peca_inicial = (maior_duplo, maior_duplo)
    maos[jogador].remove(peca_inicial)
    lado = jogar_peca(tabuleiro, pontas, peca_inicial)
    historico = [{
        "ordem": 1,
        "jogador": jogador,
        "tipo": "jogada" if maos[jogador] else "batida",
        "peca": peca_inicial,
        "lado": lado
    }]

    jogador_atual = proximo_jogador(jogador)
    ordem_jogada = 2
    passes_consecutivos = 0

    while True:
        mao = maos[jogador_atual]
        jogadas_disponiveis = jogadas_validas(mao, pontas)

        if jogadas_disponiveis:
            if jogador_atual in ["J1", "J3"]:
                peca = escolher_peca_mcts(jogador_atual, mao, jogadas_disponiveis, tabuleiro, pontas, historico)
            else:
                peca = jogadas_disponiveis[0]  # estratégia ingênua

            mao.remove(peca)
            lado = jogar_peca(tabuleiro, pontas, peca)
            tipo = "batida" if not mao else "jogada"
            historico.append({
                "ordem": ordem_jogada,
                "jogador": jogador_atual,
                "tipo": tipo,
                "peca": peca,
                "lado": lado
            })
            passes_consecutivos = 0

            if not mao:
                tipo_batida = tipo_de_batida(peca, jogador_atual, pontas)
                pontuacao = calcular_pontuacao_batida(tipo_batida)
                return jogador_atual, pontuacao

        else:
            historico.append({
                "ordem": ordem_jogada,
                "jogador": jogador_atual,
                "tipo": "passe"
            })
            passes_consecutivos += 1
            if passes_consecutivos == 4:
                vencedor, pontuacao = calcular_pontuacao_travamento(maos)
                return vencedor, pontuacao

        ordem_jogada += 1
        jogador_atual = proximo_jogador(jogador_atual)

def simular_partida_dupla_mcts(n_rodadas=100):
    duplas = {"Dupla_1": ["J1", "J3"], "Dupla_2": ["J2", "J4"]}
    pontuacao = {"Dupla_1": 0, "Dupla_2": 0}
    vitorias_jogadores = {"J1": 0, "J2": 0, "J3": 0, "J4": 0}

    for _ in range(n_rodadas):
        vencedor, pontos = simular_rodada_com_dupla_mcts()
        if vencedor is None:
            continue
        dupla_vencedora = "Dupla_1" if vencedor in duplas["Dupla_1"] else "Dupla_2"
        pontuacao[dupla_vencedora] += pontos
        vitorias_jogadores[vencedor] += 1

    print("Pontuação por dupla:", pontuacao)
    print("Vitórias por jogador:", vitorias_jogadores)

if __name__ == "__main__":
    simular_partida_dupla_mcts(n_rodadas=100)
