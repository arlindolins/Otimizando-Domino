# main.py
"""Ponto de entrada para execução simples do simulador."""


from motor_de_jogo import simular_partida

if __name__ == "__main__":
    resultado = simular_partida()
    print("Pontuação final das duplas:", resultado["duplas"])
