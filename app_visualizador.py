# app.py
from flask import Flask, jsonify, render_template
from motor_de_jogo import simular_rodada

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontend_visualizador.html')

@app.route('/simular')
def simular():
    resultado = simular_rodada()
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
