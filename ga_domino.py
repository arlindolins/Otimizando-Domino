"""ga_domino.py — Genetic Algorithm (v2)
========================================
Evolui **8 pesos** (w0‥w7) para a função‐heurística usada pela Dupla 1.
As táticas contempladas são:
  w0 ▸ bloquear adversários que podem jogar agora         (opp_can)
  w1 ▸ liberar jogada ao parceiro agora                   (partner_can)
  w2 ▸ bloquear peças prováveis dos adversários          (opp_unknown)
  w3 ▸ liberar peças prováveis do parceiro               (partner_unknown)
  w4 ▸ manter jogadas futuras na minha mão               (own_future)
  w5 ▸ descartar pips altos                              (pip_sum)
  w6 ▸ possibilidade imediata de batida valiosa          (can_finish_type)
       · 4 = cruzada, 3 = lá‑e‑lô, 2 = carroça, 1 = simples, 0 = não bate
  w7 ▸ risco de que a dupla adversária feche a **partida**
       · 1 se eles ≥ 5 pts, senão 0 — força bloqueio / travamento

Requisitos
----------
O **motor de jogo** deve oferecer:
    from motor_de_jogo import run_match_v2
onde
    wins = run_match_v2(weights: list[float], n_games: int) -> int
· `weights` é lista de 8 floats
· Retorna vitórias da Dupla 1 em `n_games` partidas

Se não existir, consulte o bloco § 6 no final: é um ‘boilerplate’ de como
adaptar rapidamente `simulate_round(weights)` para calcular as variáveis
extras e cumprir essa assinatura.
"""

from __future__ import annotations
import random
import math
import multiprocessing as mp
from collections import namedtuple
from typing import List

###############################################################################
# 1. Representação do indivíduo
###############################################################################
Individual = namedtuple("Individual", ["weights", "fitness"])
N_WEIGHTS   = 8
WEIGHT_MIN  = -30.0
WEIGHT_MAX  =  30.0
WEIGHT_BOUNDS = (WEIGHT_MIN, WEIGHT_MAX)

def random_weights() -> List[float]:
    low, high = WEIGHT_BOUNDS
    return [random.uniform(low, high) for _ in range(N_WEIGHTS)]

###############################################################################
# 2. Avaliação — ligação com motor_de_jogo.run_match_v2
###############################################################################
try:
    from motor_de_jogo import run_match_v2  # pylint: disable=import-error
except ImportError as exc:
    raise ImportError(
        "motor_de_jogo.run_match_v2 não encontrado.  "
        "Crie esta função conforme orientado no § 6 do arquivo."
    ) from exc

EVAL_GAMES = 120  # nº de partidas para avaliar cada indivíduo


def _eval(weights: List[float]) -> float:
    # taxa de vitória 0–1
    wins = run_match_v2(weights, n_games=EVAL_GAMES)
    return wins / EVAL_GAMES

###############################################################################
# 3. Operadores genéticos
###############################################################################
POP_SIZE      = 40
N_GENERATIONS = 60
ELITISM_FRACT = 0.12   # ~12 % elite
TOUR_K        = 5       # torneio
CROSS_P       = 0.9
MUT_P         = 0.25
MUT_STD       = 4.0

# Seleção ─────────────────────────────────────────────────────────────────────

def _tournament(pop):
    aspirants = random.sample(pop, TOUR_K)
    return max(aspirants, key=lambda ind: ind.fitness)

# Crossover (aritmético) ──────────────────────────────────────────────────────

def _cross(p1: Individual, p2: Individual):
    if random.random() > CROSS_P:
        return p1.weights[:], p2.weights[:]
    a = random.random()
    c1 = [a*x + (1-a)*y for x, y in zip(p1.weights, p2.weights)]
    c2 = [(1-a)*x + a*y for x, y in zip(p1.weights, p2.weights)]
    return c1, c2

# Mutação (gaussiana) ─────────────────────────────────────────────────────────

def _mutate(ws):
    lo, hi = WEIGHT_BOUNDS
    for i in range(len(ws)):
        if random.random() < MUT_P:
            ws[i] += random.gauss(0, MUT_STD)
            ws[i] = max(lo, min(hi, ws[i]))

###############################################################################
# 4. Loop GA
###############################################################################

def _init_pop():
    with mp.Pool() as pool:
        genomes = [random_weights() for _ in range(POP_SIZE)]
        fits    = pool.map(_eval, genomes)
    return [Individual(g, f) for g, f in zip(genomes, fits)]


def evolve() -> Individual:
    pop = _init_pop()
    elite_n = max(1, int(POP_SIZE * ELITISM_FRACT))

    for gen in range(N_GENERATIONS):
        pop.sort(key=lambda ind: ind.fitness, reverse=True)
        elite = pop[:elite_n]

        # gerar filhos
        children_genomes = []
        while len(children_genomes) < POP_SIZE - elite_n:
            p1, p2 = _tournament(pop), _tournament(pop)
            c1, c2 = _cross(p1, p2)
            _mutate(c1)
            _mutate(c2)
            children_genomes.extend([c1, c2])
        children_genomes = children_genomes[: POP_SIZE - elite_n]

        with mp.Pool() as pool:
            fits = pool.map(_eval, children_genomes)
        children = [Individual(g, f) for g, f in zip(children_genomes, fits)]

        pop = elite + children
        best = pop[0]
        avg  = sum(ind.fitness for ind in pop) / POP_SIZE
        print(f"Gen {gen:02} | best={best.fitness:.3f} | avg={avg:.3f}")

    pop.sort(key=lambda ind: ind.fitness, reverse=True)
    return pop[0]

###############################################################################
# 5. Execução direta ==========================================================
###############################################################################
if __name__ == "__main__":
    champion = evolve()
    print("\n=== Pesos ótimos encontrados ===")
    for i, w in enumerate(champion.weights):
        print(f"w{i} = {w:.2f}")
    print(f"Fitness = {champion.fitness:.3f}")

###############################################################################
# 6. Snippet de integração rápida (cole no motor se precisar)==================
###############################################################################
# def run_match_v2(weights, n_games=120):
#     """Interface requerida pelo GA.  Ajuste simulate_round_v2 conforme abaixo."""
#     vitorias = 0
#     for _ in range(n_games):
#         vencedor = simulate_round_v2(weights)  # sua função de simular 1 rodada
#         if vencedor in (0, 2):
#             vitorias += 1
#     return vitorias
#
# Onde `simulate_round_v2(weights)` é igual ao atual simulate_round, mas:
#   • passa `weights` à estratégia da Dupla 1
#   • dentro da estratégia calcule:
#       opp_can, partner_can, opp_unknown, partner_unknown,
#       own_future, pip_sum, can_finish_type, enemy_close_to_game
#   • retorne o vencedor da **rodada** (player 0‑3)
# Para pontuação da *partida* (até 6 pts) repita as rodadas dentro de
# run_match_v2 ou ajuste a sua própria lógica de campeonato.
###############################################################################
