# domino_v3.py
import random
from collections import deque
import csv
import os
import uuid
import time
from typing import List, Dict, Optional
from core.peca import Peca
from core.jogador import Jogador
from core.tabuleiro import Tabuleiro
from core.dupla import Dupla
from utilidades.distribuicao import distribuir_jogadores
from regras.game_logic import (
    proximo_jogador_obj,
    determinar_tipo_batida,
    pontuacao_por_tipo,
    determinar_vencedor_travamento,
)

def simular_rodada(
    jogadores: List[Jogador],
    jogador_inicial_nome: Optional[str] = None,
    *,
    duplas: dict[str, Dupla] | None = None,
    pontos_para_vencer: int = 6,
):
    tabuleiro = Tabuleiro()
    historico = []
    estados = []
    ordem_jogada = 1
    passes_por_jogador = {j.nome: 0 for j in jogadores}

    # Identificar o jogador com o maior duplo (se não especificado)
    if jogador_inicial_nome is None:
        maior_duplo = -1
        jogador_inicial = None
        for j in jogadores:
            for p in j.mao:
                if p.is_duplo() and p.lado1 > maior_duplo:
                    maior_duplo = p.lado1
                    jogador_inicial = j
        if not jogador_inicial:
            return {"erro": "Nenhum duplo encontrado"}
    else:
        jogador_inicial = next(j for j in jogadores if j.nome == jogador_inicial_nome)

    jogador_atual = jogador_inicial
    motivo_fim = None
    tipo_batida = None
    vencedor_rodada = None
    pontuacao_rodada = 0

    while True:
        jogadas = jogador_atual.jogadas_validas(tabuleiro.obter_pontas())

        if jogadas:
            if ordem_jogada == 1 and jogador_inicial_nome is None:
                # Primeira jogada: deve ser o maior duplo
                peca_jogada = next(p for p in jogador_atual.mao if p.is_duplo() and p.lado1 == maior_duplo)
            else:
                peca_jogada = jogador_atual.escolher_peca(
                    tabuleiro,
                    jogadores,
                    duplas=duplas or {},
                    passes_jog=passes_por_jogador,
                    pontos_para_vencer=pontos_para_vencer,
                )

            jogador_atual.remover_peca(peca_jogada)
            lado = tabuleiro.jogar(peca_jogada)
            tipo = "batida" if not jogador_atual.mao else "jogada"

            historico.append({
                "ordem": ordem_jogada,
                "jogador": jogador_atual.nome,
                "tipo": tipo,
                "peca": (peca_jogada.lado1, peca_jogada.lado2),
                "lado": lado
            })

            tabuleiro.resetar_passes()

            if not jogador_atual.mao:
                tipo_batida = determinar_tipo_batida(peca_jogada, tabuleiro.obter_pontas())
                pontuacao_rodada = pontuacao_por_tipo(tipo_batida)
                vencedor_rodada = jogador_atual.nome
                motivo_fim = "batida"

        else:
            historico.append({
                "ordem": ordem_jogada,
                "jogador": jogador_atual.nome,
                "tipo": "passe"
            })
            passes_por_jogador[jogador_atual.nome] += 1
            jogador_atual.registrar_passe(tabuleiro.obter_pontas())
            tabuleiro.registrar_passe()

            if tabuleiro.passes_consecutivos == 4:
                vencedor_rodada, pontuacao_rodada = determinar_vencedor_travamento(jogadores)
                motivo_fim = "travamento"
                tipo_batida = "travamento"

        estados.append({
            "ordem_jogada": ordem_jogada,
            "jogador": jogador_atual.nome,
            "tipo": historico[-1]["tipo"],
            "peca": historico[-1].get("peca"),
            "lado": historico[-1].get("lado"),
            "tabuleiro": [(p.lado1, p.lado2) for p in tabuleiro.pecas],
            "maos": {j.nome: [(p.lado1, p.lado2) for p in j.mao] for j in jogadores},
            "tipo_batida": tipo_batida,
            "motivo_fim": motivo_fim,
            "vencedor_rodada": vencedor_rodada,
            "jogadas": historico,
            "jogadas_disponiveis": [(p.lado1, p.lado2) for p in jogadas]
        })

        if motivo_fim:
            break

        ordem_jogada += 1
        jogador_atual = proximo_jogador_obj(jogadores, jogador_atual)

    return {
        "estados": estados,
        "final": {
            "tipo_batida": tipo_batida,
            "motivo_fim": motivo_fim,
            "vencedor_rodada": vencedor_rodada,
            "pontuacao_rodada": pontuacao_rodada
        }
    }


def simular_partida(
    pontos_para_vencer: int = 6,
    pontuacao_por_jogador: Optional[dict] = None,
    estrategias: Optional[dict] = None,
) -> dict:
    """Simula uma partida completa.

    Parameters
    ----------
    pontos_para_vencer: int
        Pontuação alvo para que uma dupla vença a partida.
    pontuacao_por_jogador: dict | None
        Dicionário opcional para acumular a pontuação ao longo de múltiplas
        partidas.
    estrategias: dict | None
        Mapeamento ``nome_jogador -> estratégia`` a ser utilizado na
        distribuição das peças. Valores podem ser callables, objetos com
        ``escolher_peca`` ou subclasses de :class:`Jogador`.
    """
    # Define as duplas
    duplas = {
        "Dupla_1": Dupla("Dupla_1", ["J1", "J3"]),
        "Dupla_2": Dupla("Dupla_2", ["J2", "J4"])
    }

    pontuacao_por_jogador = {nome: 0 for dupla in duplas.values() for nome in dupla.jogadores}

    rodadas = []
    jogador_inicial_nome = None  # definido dinamicamente a cada rodada

    # Loop principal
    while max(dupla.pontuacao for dupla in duplas.values()) < pontos_para_vencer:
        jogadores = distribuir_jogadores(estrategias)  # retorna List[Jogador]
        rodada = simular_rodada(
            jogadores,
            jogador_inicial_nome=jogador_inicial_nome,
            duplas=duplas,
            pontos_para_vencer=pontos_para_vencer,
        )

        if "erro" in rodada:
            continue  # refaz a rodada

        rodadas.append(rodada)
        final = rodada["final"]
        jogador_vencedor = final["vencedor_rodada"]
        pontos = final["pontuacao_rodada"]

        if jogador_vencedor:
            jogador_inicial_nome = jogador_vencedor  # define início da próxima rodada

            if duplas["Dupla_1"].contem_jogador(jogador_vencedor):
                duplas["Dupla_1"].adicionar_pontos(pontos)
            else:
                duplas["Dupla_2"].adicionar_pontos(pontos)

            pontuacao_por_jogador[jogador_vencedor] += pontos

        # Permite que estratégias aprendizes atualizem seus parâmetros
        for j in jogadores:
            estrategia = getattr(j, "estrategia", None)
            if hasattr(estrategia, "notificar_resultado"):
                estrategia.notificar_resultado(j.nome, jogador_vencedor)

    vencedor_partida = max(duplas.items(), key=lambda item: item[1].pontuacao)[0]

    return {
        "duplas": {nome: dupla.pontuacao for nome, dupla in duplas.items()},
        "pontuacao_por_jogador": pontuacao_por_jogador,
        "rodadas": rodadas,
        "vencedor_partida": vencedor_partida
    }


def salvar_resultado_em_csv(
    id_partida: str,
    resultado: dict,
    writer_partidas: csv.writer,
    writer_rodadas: csv.writer,
    writer_jogadas: csv.writer,
) -> None:
    """Registra o resultado de ``simular_partida`` em arquivos CSV já abertos."""

    writer_partidas.writerow(
        [
            id_partida,
            resultado["vencedor_partida"],
            resultado["pontuacao_por_jogador"]["J1"],
            resultado["pontuacao_por_jogador"]["J2"],
            resultado["pontuacao_por_jogador"]["J3"],
            resultado["pontuacao_por_jogador"]["J4"],
        ]
    )

    for id_rodada, rodada in enumerate(resultado["rodadas"]):
        final = rodada["final"]
        writer_rodadas.writerow(
            [
                id_partida,
                id_rodada,
                rodada["estados"][0]["jogador"],
                final["tipo_batida"],
                final["motivo_fim"],
                final["vencedor_rodada"],
                final["pontuacao_rodada"],
                resultado["pontuacao_por_jogador"]["J1"],
                resultado["pontuacao_por_jogador"]["J2"],
                resultado["pontuacao_por_jogador"]["J3"],
                resultado["pontuacao_por_jogador"]["J4"],
            ]
        )

        for estado in rodada["estados"]:
            if estado["tipo"] in ["jogada", "batida"] and estado["peca"]:
                x, y = estado["peca"]
            else:
                x, y = "", ""
            writer_jogadas.writerow(
                [
                    id_partida,
                    id_rodada,
                    estado["ordem_jogada"],
                    estado["jogador"],
                    estado["tipo"],
                    x,
                    y,
                    estado.get("lado", ""),
                ]
            )

pontuacao_jogadores = {"J1": 0, "J2": 0, "J3": 0, "J4": 0}

# NOVA FUNÇÃO PARA SALVAR O HISTÓRICO COMPLETO DAS PARTIDAS

def simular_varias_partidas_em_csv(n=10, pasta_destino="historico_csv"):
    os.makedirs(pasta_destino, exist_ok=True)
    
    partidas_csv = open(os.path.join(pasta_destino, "partidas.csv"), mode="w", newline="")
    rodadas_csv = open(os.path.join(pasta_destino, "rodadas.csv"), mode="w", newline="")
    jogadas_csv = open(os.path.join(pasta_destino, "jogadas.csv"), mode="w", newline="")

    writer_partidas = csv.writer(partidas_csv)
    writer_rodadas = csv.writer(rodadas_csv)
    writer_jogadas = csv.writer(jogadas_csv)

    writer_partidas.writerow(["id_partida", "vencedor_partida", "pontuacao_J1", "pontuacao_J2", "pontuacao_J3", "pontuacao_J4"])
    writer_rodadas.writerow(["id_partida", "id_rodada", "inicio_rodada", "tipo_batida", "motivo_fim", "vencedor_rodada", "pontuacao_rodada", "pontuacao_J1", "pontuacao_J2", "pontuacao_J3", "pontuacao_J4"])
    writer_jogadas.writerow(["id_partida", "id_rodada", "ordem_jogada", "jogador", "tipo", "peca_x", "peca_y", "lado"])


    for _ in range(n):
        id_partida = str(uuid.uuid4())
        resultado = simular_partida(pontuacao_por_jogador=pontuacao_jogadores)
        salvar_resultado_em_csv(
            id_partida,
            resultado,
            writer_partidas,
            writer_rodadas,
            writer_jogadas,
        )

    partidas_csv.close()
    rodadas_csv.close()
    jogadas_csv.close()

    
    print("\nExportação concluída. Arquivos salvos em:", pasta_destino)
    

if __name__ == "__main__":
    
    inicio = time.time()
    simular_varias_partidas_em_csv(n=10)
    fim = time.time()
    print(f"Tempo total de execução: {fim - inicio:.2f} segundos")
