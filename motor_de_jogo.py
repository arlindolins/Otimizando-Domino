# domino_v3.py
import random
from collections import deque
import copy
import json
import csv
import os
import uuid
import time


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
    
    return jogador_inicial, maior_duplo


def proximo_jogador(jogador_atual):
    ordem = ["J1", "J2", "J3", "J4"]
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
    jogador, maior_duplo = jogador_com_maior_duplo(maos)


    if jogador is None:
        return {"erro": "Nenhum duplo encontrado"}

    passes_consecutivos = 0
    vencedor_rodada = None
    motivo_fim = None
    tipo_batida = None
    pontuacao_rodada = 0

    while True:
        mao = maos[jogador]
        jogadas_disponiveis = jogadas_validas(mao, pontas)
        jogadas = jogadas_disponiveis.copy()

        if jogadas:

            if ordem_jogada == 1:
                    peca = (maior_duplo,maior_duplo)
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
            else:
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
                passes_consecutivos = 0
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
            "jogadas": copy.deepcopy(historico),
            "jogadas_disponiveis": jogadas_disponiveis

        })

        if motivo_fim:
            break

        ordem_jogada += 1
        jogador = proximo_jogador(jogador)

    return {
        "estados": estados,
        "final": {
            "tipo_batida": tipo_batida,
            "motivo_fim": motivo_fim,
            "vencedor_rodada": vencedor_rodada,
            "pontuacao_rodada": pontuacao_rodada
        }
        
    }
def simular_partida(pontuacao_por_jogador=None):
    
    
    duplas = {
        "Dupla_1": ["J1", "J3"],
        "Dupla_2": ["J2", "J4"]
    }
    pontuacao = {
        "Dupla_1": 0,
        "Dupla_2": 0
    }
    if pontuacao_por_jogador is None:
        pontuacao_por_jogador = {jogador: 0 for dupla in duplas.values() for jogador in dupla}

    rodadas = []
    vencedor_partida = None
    pontos_para_vencer = 6

    while max(pontuacao.values()) < pontos_para_vencer:
        rodada = simular_rodada()

        if "erro" in rodada:
            continue

        info = rodada["final"]
        rodadas.append(rodada)

        jogador = info["vencedor_rodada"]
        pontos = info["pontuacao_rodada"]

        if jogador:
            dupla_vencedora = "Dupla_1" if jogador in duplas["Dupla_1"] else "Dupla_2"
            pontuacao[dupla_vencedora] += pontos

    vencedor_partida = max(pontuacao, key=pontuacao.get)

    # ✅ Atualiza pontuação por jogador
    for jogador in duplas[vencedor_partida]:
        pontuacao_por_jogador[jogador] += 1

    return {
        "duplas": duplas,
        "pontuacao": pontuacao,
        "pontuacao_por_jogador": pontuacao_por_jogador,
        "rodadas": rodadas,
        "vencedor_partida": vencedor_partida
    }

# NOVA FUNÇÃO PARA SALVAR O HISTÓRICO COMPLETO DAS PARTIDAS

def simular_varias_partidas_em_csv(n=10000, pasta_destino="historico_csv"):
    os.makedirs(pasta_destino, exist_ok=True)
    
    partidas_csv = open(os.path.join(pasta_destino, "partidas.csv"), mode="w", newline="")
    rodadas_csv = open(os.path.join(pasta_destino, "rodadas.csv"), mode="w", newline="")
    jogadas_csv = open(os.path.join(pasta_destino, "jogadas.csv"), mode="w", newline="")

    writer_partidas = csv.writer(partidas_csv)
    writer_rodadas = csv.writer(rodadas_csv)
    writer_jogadas = csv.writer(jogadas_csv)

    writer_partidas.writerow(["id_partida", "vencedor_partida", "pontuacao_J1", "pontuacao_J2", "pontuacao_J3", "pontuacao_J4"])
    writer_rodadas.writerow(["id_partida", "id_rodada", "inicio_rodada", "tipo_batida", "motivo_fim", "vencedor_rodada", "pontuacao_rodada"])
    writer_jogadas.writerow(["id_partida", "id_rodada", "ordem_jogada", "jogador", "tipo", "peca_x", "peca_y", "lado"])

    pontuacao_jogadores = {"J1": 0, "J2": 0, "J3": 0, "J4": 0}

    
    for _ in range(n):
        id_partida = str(uuid.uuid4())
        resultado = simular_partida(pontuacao_por_jogador=pontuacao_jogadores)

        writer_partidas.writerow([
            id_partida,
            resultado["vencedor_partida"],
            resultado["pontuacao_por_jogador"]["J1"],
            resultado["pontuacao_por_jogador"]["J2"],
            resultado["pontuacao_por_jogador"]["J3"],
            resultado["pontuacao_por_jogador"]["J4"]
        ])

        for id_rodada, rodada in enumerate(resultado["rodadas"]):
            final = rodada["final"]
            writer_rodadas.writerow([
                id_partida,
                id_rodada,
                rodada["estados"][0]["jogador"],
                final["tipo_batida"],
                final["motivo_fim"],
                final["vencedor_rodada"],
                final["pontuacao_rodada"]
            ])

            for estado in rodada["estados"]:
                if estado["tipo"] in ["jogada", "batida"] and estado["peca"]:
                    x, y = estado["peca"]
                else:
                    x, y = "", ""
                writer_jogadas.writerow([
                    id_partida,
                    id_rodada,
                    estado["ordem_jogada"],
                    estado["jogador"],
                    estado["tipo"],
                    x,
                    y,
                    estado.get("lado", "")
                ])

    partidas_csv.close()
    rodadas_csv.close()
    jogadas_csv.close()

    
    print("\nExportação concluída. Arquivos salvos em:", pasta_destino)
    

if __name__ == "__main__":
    
    inicio = time.time()
    simular_varias_partidas_em_csv(n=10000)
    fim = time.time()
    print(f"Tempo total de execução: {fim - inicio:.2f} segundos")
