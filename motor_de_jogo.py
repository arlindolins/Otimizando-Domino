# domino_v3.py
import random
from collections import deque
import copy

def gerar_pecas():
    return [(i, j) for i in range(7) for j in range(i, 7)]

def distribuir_pecas():
    pecas = gerar_pecas()
    random.shuffle(pecas)
    maos = {
        "J1": sorted(pecas[0:6]),
        "J2": sorted(pecas[6:12]),
        "J3": sorted(pecas[12:18]),
        "J4": sorted(pecas[18:24])
    }
    pecas_fora = pecas[24:]
    return maos, pecas_fora

def jogador_com_maior_duplo(maos):
    maior_duplo = -1
    jogador_inicial = None
    for jogador, mao in maos.items():
        for peca in mao:
            if peca[0] == peca[1] and peca[0] > maior_duplo:
                maior_duplo = peca[0]
                jogador_inicial = jogador
    return jogador_inicial

def proximo_jogador(jogador_atual):
    ordem = ["J1", "J4", "J3", "J2"]
    idx = ordem.index(jogador_atual)
    return ordem[(idx + 1) % 4]

def jogadas_validas(mao, pontas):
    if pontas[0] is None:
        return mao
    return [peca for peca in mao if peca[0] in pontas or peca[1] in pontas]

def jogar_peca(tabuleiro, pontas, peca):
    if not tabuleiro:
        tabuleiro.append(peca)
        pontas[0], pontas[1] = peca
        return "inicial"
    if peca[0] == pontas[0]:
        tabuleiro.appendleft((peca[1], peca[0]))
        pontas[0] = peca[1]
        return "esquerda"
    elif peca[1] == pontas[0]:
        tabuleiro.appendleft(peca)
        pontas[0] = peca[0]
        return "esquerda"
    elif peca[0] == pontas[1]:
        tabuleiro.append(peca)
        pontas[1] = peca[1]
        return "direita"
    elif peca[1] == pontas[1]:
        tabuleiro.append((peca[1], peca[0]))
        pontas[1] = peca[0]
        return "direita"

def tipo_de_batida(peca_final, jogador, pontas):
    eh_duplo = peca_final[0] == peca_final[1]
    encaixa_esquerda = (peca_final[0] == pontas[0]) or (peca_final[1] == pontas[0])
    encaixa_direita = (peca_final[0] == pontas[1]) or (peca_final[1] == pontas[1])
    encaixa_ambas = encaixa_esquerda and encaixa_direita

    if eh_duplo and encaixa_ambas:
        return "cruzada"
    elif not eh_duplo and encaixa_ambas and pontas[0] != pontas[1]:
        return "la_e_lo"
    elif eh_duplo:
        return "carroca"
    elif encaixa_direita or encaixa_esquerda:
        return "simples"

def calcular_pontuacao_batida(tipo_batida):
    return {
        "simples": 1,
        "carroca": 2,
        "la_e_lo": 3,
        "cruzada": 4
    }.get(tipo_batida, 0)

def calcular_pontuacao_travamento(maos):
    soma_maos = {j: sum(p[0] + p[1] for p in mao) for j, mao in maos.items()}
    vencedor = min(soma_maos, key=soma_maos.get)
    menores = [j for j, s in soma_maos.items() if s == soma_maos[vencedor]]
    if len(menores) > 1:
        return None, 0
    return vencedor, 1

def simular_rodada():
    maos, _ = distribuir_pecas()
    tabuleiro = deque()
    pontas = [None, None]
    historico = []
    estados = []
    ordem_jogada = 1
    jogador = jogador_com_maior_duplo(maos)

    if jogador is None:
        return {"erro": "Nenhum duplo encontrado"}

    passes_consecutivos = 0
    vencedor_rodada = None
    motivo_fim = None
    tipo_batida = None
    pontuacao_rodada = 0

    while True:
        mao = maos[jogador]
        jogadas = jogadas_validas(mao, pontas)

        if jogadas:
            peca = jogadas[0]
            mao.remove(peca)
            lado = jogar_peca(tabuleiro, pontas, peca)
            tipo = "batida" if not mao else "jogada"
            historico.append({
                "ordem": ordem_jogada,
                "jogador": jogador,
                "tipo": tipo,
                "peca": peca,
                "lado": lado
            })
            if not mao:
                tipo_batida = tipo_de_batida(peca, jogador, pontas)
                pontuacao_rodada = calcular_pontuacao_batida(tipo_batida)
                vencedor_rodada = jogador
                motivo_fim = "batida"
        else:
            historico.append({
                "ordem": ordem_jogada,
                "jogador": jogador,
                "tipo": "passe"
            })
            passes_consecutivos += 1
            if passes_consecutivos == 4:
                vencedor_rodada, pontuacao_rodada = calcular_pontuacao_travamento(maos)
                motivo_fim = "travamento"
                tipo_batida = "travamento"

        estados.append({
            "ordem_jogada": ordem_jogada,
            "jogador": jogador,
            "tipo": historico[-1]["tipo"],
            "peca": historico[-1].get("peca"),
            "lado": historico[-1].get("lado"),
            "tabuleiro": list(tabuleiro),
            "maos": copy.deepcopy(maos),
            "tipo_batida": tipo_batida,
            "motivo_fim": motivo_fim,
            "vencedor_rodada": vencedor_rodada,
            "jogadas": copy.deepcopy(historico)
        })

        if motivo_fim:
            break

        ordem_jogada += 1
        jogador = proximo_jogador(jogador)

    print(estados)
    
    return {
        "estados": estados,
        "final": {
            "tipo_batida": tipo_batida,
            "motivo_fim": motivo_fim,
            "vencedor_rodada": vencedor_rodada,
            "pontuacao_rodada": pontuacao_rodada
        }
    }


    

