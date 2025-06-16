# main.py
"""Ponto de entrada para execução simples do simulador."""


from motor_de_jogo import simular_partida
from core.jogador import escolher_peca_ga, MCTSJogador, RLJogador

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

estrategias = {
    "J1": None,
    "J3": None,
    #"J1": lambda j, t, js: escolher_peca_ga(j, t, js, pesos),
    #"J3": lambda j, t, js: escolher_peca_ga(j, t, js, pesos),
    "J2": RLJogador,
    "J4": RLJogador,
}

n_games = 100


if __name__ == "__main__":
    
    vitoriasD1 = 0
    vitoriasD2 = 0
    for _ in range(n_games):
        resultado = simular_partida(estrategias=estrategias)
        if resultado["vencedor_partida"] == "Dupla_1":
            vitoriasD1 += 1
        elif resultado["vencedor_partida"] == "Dupla_2":
            vitoriasD2 += 1
    print("Pontuação final das duplas:", vitoriasD1, vitoriasD2)
