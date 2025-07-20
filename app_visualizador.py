from flask import Flask, request, jsonify, render_template
from core.jogador import Jogador, RLJogador, GAJogador, MCTSJogador, CLIJogador
from motor_de_jogo import simular_partida

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontend_visualizador.html')

@app.route('/simular', methods=['POST'])
def simular():
    # 1. Recebe exatamente {"J1": "...", "J2": "...", "J3": "...", "J4": "..."}
    data = request.get_json()
    
    # 2. Constrói a fábrica de estratégia a partir da string
    def construir_estrategia(tipo: str):
        if tipo == "RL":
            return RLJogador
        elif tipo == "GA":
            pesos = [1.8, 15.3, 15.7, 9.4, -9.6, -1.5, -20.4, 6.4]
            return lambda nome, mao: GAJogador(nome, mao, pesos)
        elif tipo == "MCTS":
            return lambda nome, mao: MCTSJogador(nome, mao)
        elif tipo == "Aleatório":
            return Jogador
        elif tipo == "Controlar jogador":
            return CLIJogador
        # fallback seguro
        return Jogador

    # 3. Garante as quatro entradas J1–J4, usando exatamente o que veio do frontend
    jogadores = ["J1", "J2", "J3", "J4"]
    estrategias = {
        j: construir_estrategia(data.get(j, "Aleatório"))
        for j in jogadores
    }

    # 4. Executa a simulação da partida
    resultado = simular_partida(estrategias=estrategias)

    # 5. Transforma o resultado para o formato esperado pelo frontend
    estados = []
    historicoRodadas = []
    placar = {
        "Dupla_1": resultado["duplas"]["Dupla_1"],
        "Dupla_2": resultado["duplas"]["Dupla_2"]
    }

    for rodada in resultado["rodadas"]:
        estados.extend(rodada["estados"])
        final = rodada["final"]
        if final["vencedor_rodada"]:
            dupla = "Dupla_1" if final["vencedor_rodada"] in ["J1", "J3"] else "Dupla_2"
            historicoRodadas.append({
                "vencedor": final["vencedor_rodada"],
                "tipoBatida": final["tipo_batida"],
                "pontos": final["pontuacao_rodada"],
                "dupla": dupla
            })

    return jsonify({
        "estados": estados,
        "placar": placar,
        "historicoRodadas": historicoRodadas,
        "vencedor_partida": resultado["vencedor_partida"]
    })

if __name__ == '__main__':
    app.run(debug=True)
