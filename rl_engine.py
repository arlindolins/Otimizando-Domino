from __future__ import annotations

import os
import pickle
import random
from collections import defaultdict
from typing import Tuple

from core.jogador import Jogador
from core.tabuleiro import Tabuleiro
from core.peca import Peca

class RLDominoStrategy:
    """Estrategia simples de aprendizado por reforço.

    A cada jogada, um valor ``Q`` é associado ao estado (pontas e peças na
    mão) e à peça escolhida. Ao final de cada rodada o valor é atualizado de
    acordo com o resultado da rodada, permitindo que o agente aprenda
    progressivamente sem conhecimento prévio.

    O objeto pode opcionalmente persistir os valores aprendidos em disco.
    """

    def __init__(self, alpha: float = 0.1, epsilon: float = 0.1, persistence_file: str | None = None):
        self.alpha = alpha
        self.epsilon = epsilon
        self.q: defaultdict[Tuple, float] = defaultdict(float)
        self.prev_state: Tuple | None = None
        self.prev_action: Tuple[int, int] | None = None
        self._file = persistence_file
        if self._file:
            self._load(self._file)

    def _state(self, jogador: Jogador, tabuleiro: Tabuleiro) -> Tuple:
        pontas = tabuleiro.obter_pontas()
        mao = tuple(sorted((p.lado1, p.lado2) for p in jogador.mao))
        return pontas, mao

    def escolher_peca(self, jogador: Jogador, tabuleiro: Tabuleiro, jogadores):
        jogadas = jogador.jogadas_validas(tabuleiro.obter_pontas())
        if not jogadas:
            raise ValueError("Jogador não possui jogadas válidas")

        estado = self._state(jogador, tabuleiro)
        if random.random() < self.epsilon:
            escolha = random.choice(jogadas)
        else:
            valores = [self.q[(estado, (p.lado1, p.lado2))] for p in jogadas]
            max_v = max(valores)
            melhores = [p for p, v in zip(jogadas, valores) if v == max_v]
            escolha = random.choice(melhores)

        self.prev_state = estado
        self.prev_action = (escolha.lado1, escolha.lado2)
        return escolha

    def notificar_resultado(self, jogador_nome: str, vencedor: str | None):
        if self.prev_state is None:
            return
        recompensa = 1.0 if vencedor == jogador_nome else -1.0 if vencedor else 0.0
        chave = (self.prev_state, self.prev_action)
        self.q[chave] += self.alpha * (recompensa - self.q[chave])
        self.prev_state = None
        self.prev_action = None

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------
    def save(self, path: str | None = None) -> None:
        """Salva os valores aprendidos em ``path``.

        Se ``path`` for ``None`` utiliza o caminho definido na inicialização.
        """
        target = path or self._file
        if target is None:
            raise ValueError("Um caminho para salvar deve ser fornecido")
        with open(target, "wb") as f:
            pickle.dump(dict(self.q), f)
        self._file = target

    def _load(self, path: str) -> None:
        """Carrega valores previamente salvos, se disponíveis."""
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
            self.q = defaultdict(float, data)
        else:
            self.q = defaultdict(float)

    def load(self, path: str) -> None:
        """Sobrescreve o arquivo de persistência e carrega seus dados."""
        self._load(path)
        self._file = path
