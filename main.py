# main.py
"""Ponto de entrada para execução simples do simulador."""


from concurrent.futures import ProcessPoolExecutor

from motor_de_jogo import simular_partida
from core.jogador import escolher_peca_ga, MCTSJogador

# Pesos otimizados em 60 gerações
w0 = 1.83
w1 = 15.30
w2 = 15.69
w3 = 9.43
w4 = -9.64
w5 = -1.47
w6 = -20.42
w7 = 6.37

# substitua pelos seus oito pesos
pesos = [w0, w1, w2, w3, w4, w5, w6, w7]

def estrategia_ga(jogador, tabuleiro, jogadores, *, pesos=pesos, **_):
    """Wrapper para permitir uso com ``multiprocessing``."""
    return escolher_peca_ga(jogador, tabuleiro, jogadores, pesos)


estrategias = {
    "J1": estrategia_ga,
    "J3": estrategia_ga,
    "J2": MCTSJogador,
    "J4": MCTSJogador,
}

n_games = 100

if __name__ == "__main__":
    def _run(_):
        return simular_partida(estrategias=estrategias)["vencedor_partida"]

    with ProcessPoolExecutor() as executor:
        resultados = list(executor.map(_run, range(n_games)))

    vitoriasD1 = sum(r == "Dupla_1" for r in resultados)
    vitoriasD2 = sum(r == "Dupla_2" for r in resultados)
    print("Pontuação final das duplas:", vitoriasD1, vitoriasD2)
