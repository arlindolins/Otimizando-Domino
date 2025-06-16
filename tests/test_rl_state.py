import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.peca import Peca
from core.jogador import Jogador
from core.dupla import Dupla
from core.tabuleiro import Tabuleiro
from rl_engine import RLDominoStrategy


def test_imports():
    importlib.import_module('motor_de_jogo')
    importlib.import_module('rl_engine')


def test_state_encoder():
    strat = RLDominoStrategy(epsilon=0.0)
    j1 = Jogador('J1', [Peca(6, 6), Peca(5, 4)], estrategia=strat)
    j2 = Jogador('J2', [Peca(0, 1)])
    j3 = Jogador('J3', [Peca(2, 2)])
    j4 = Jogador('J4', [Peca(3, 5)])
    jogadores = [j1, j2, j3, j4]
    tabuleiro = Tabuleiro()
    duplas = {
        'Dupla_1': Dupla('Dupla_1', ['J1', 'J3']),
        'Dupla_2': Dupla('Dupla_2', ['J2', 'J4']),
    }
    passes = {j.nome: 0 for j in jogadores}
    state = strat._state(j1, tabuleiro, jogadores, duplas, passes, 6)
    assert len(state) == 47
    assert state[0] == -1
    assert state[11] == 1
    assert state[12] == 6
    assert state[41] == 0
    assert state[42] == 1


def test_simulation_runs():
    from motor_de_jogo import simular_partida

    s1 = RLDominoStrategy(epsilon=0.2)
    s2 = RLDominoStrategy(epsilon=0.2)
    for _ in range(10):
        simular_partida(pontos_para_vencer=2, estrategias={'J1': s1, 'J3': s2})
    assert len(s1.q) > 0

