from __future__ import annotations

import os
import pickle
import random
from collections import defaultdict
from typing import Tuple, Sequence

from core.jogador import Jogador
from core.tabuleiro import Tabuleiro
from core.peca import Peca
from core.dupla import Dupla

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

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    @staticmethod
    def _bucket(x: int, bounds: Sequence[int]) -> int:
        for i, b in enumerate(bounds):
            if x <= b:
                return i
        return len(bounds)

    @staticmethod
    def _encode_mask(values: Sequence[int]) -> int:
        mask = 0
        for v in values:
            mask |= 1 << v
        return mask

    def _state(
        self,
        jogador: Jogador,
        tabuleiro: Tabuleiro,
        jogadores: Sequence[Jogador],
        duplas: dict[str, Dupla],
        passes_jog: dict[str, int],
        pontos_para_vencer: int,
    ) -> tuple[int, ...]:
        pontas = tabuleiro.obter_pontas()
        p0 = pontas[0] if pontas[0] is not None else -1
        p1 = pontas[1] if pontas[1] is not None else -1
        diff = p0 - p1 if p0 != -1 and p1 != -1 else -1

        both_playable = int(
            not tabuleiro.esta_vazio()
            and any(
                p.encaixa(pontas[0]) and p.encaixa(pontas[1])
                for p in jogador.mao
            )
        )

        hist = [0] * 7
        n_duplos = 0
        max_duplo = -1
        soma_pips = 0
        for p in jogador.mao:
            hist[p.lado1] += 1
            hist[p.lado2] += 1
            if p.is_duplo():
                n_duplos += 1
                max_duplo = max(max_duplo, p.lado1)
            soma_pips += p.valor_total()
        sum_bucket = self._bucket(soma_pips, [10, 20])
        len_mao = len(jogador.mao)

        if tabuleiro.esta_vazio():
            n_left = n_right = n_total = len_mao
        else:
            left, right = pontas
            n_left = sum(p.encaixa(left) for p in jogador.mao)
            n_right = sum(p.encaixa(right) for p in jogador.mao)
            n_total = sum(p.encaixa(left) or p.encaixa(right) for p in jogador.mao)

        restantes = tabuleiro.restantes_por_valor()
        remaining_bucket = [self._bucket(r, [0, 1, 3]) for r in restantes]
        closed_mask = self._encode_mask([i for i, r in enumerate(restantes) if r == 0])

        idx = jogadores.index(jogador)
        ordem = [
            jogadores[(idx + 2) % len(jogadores)],
            jogadores[(idx + 1) % len(jogadores)],
            jogadores[(idx + 2) % len(jogadores)],
            jogadores[(idx + 3) % len(jogadores)],
        ]
        hand_sizes = [len(p.mao) for p in ordem]
        passes = [passes_jog.get(p.nome, 0) for p in ordem]
        masks = [
            self._encode_mask(p.valores_comprovadamente_ausentes()) for p in ordem
        ]

        minha_dupla = None
        for nome, dupla in duplas.items():
            if dupla.contem_jogador(jogador.nome):
                minha_dupla = nome
                break
        dupla_pontos = duplas[minha_dupla].pontuacao if minha_dupla else 0
        outra = [d for d in duplas.values() if not d.contem_jogador(jogador.nome)][0]
        score_diff = (dupla_pontos > outra.pontuacao) - (
            dupla_pontos < outra.pontuacao
        )

        points_to_win_bucket = self._bucket(
            max(pontos_para_vencer - dupla_pontos, 0),
            [30, 60],
        )
        rounds_left_bucket = 3

        my_one_left = int(len_mao <= 1)
        enemy_one_left = int(any(len(p.mao) <= 1 for p in jogadores if p is not jogador))
        lock_imminent = int(tabuleiro.passes_consecutivos >= 2)

        rem = restantes
        both_critical = int(
            not tabuleiro.esta_vazio()
            and rem[pontas[0]] <= 1
            and rem[pontas[1]] <= 1
        )
        played_counts = tabuleiro.contagem_por_valor()
        pip_dominant = int(any(c >= 5 for c in played_counts))
        partner = ordem[0]
        partner_can_play = int(partner.possui_jogada(tabuleiro.obter_pontas()))

        return (
            p0,
            p1,
            diff,
            both_playable,
            *hist,
            n_duplos,
            max_duplo,
            sum_bucket,
            len_mao,
            n_left,
            n_right,
            n_total,
            *remaining_bucket,
            closed_mask,
            *hand_sizes,
            *passes,
            *masks,
            score_diff,
            points_to_win_bucket,
            rounds_left_bucket,
            my_one_left,
            enemy_one_left,
            lock_imminent,
            both_critical,
            pip_dominant,
            partner_can_play,
        )

    def escolher_peca(
        self,
        jogador: Jogador,
        tabuleiro: Tabuleiro,
        jogadores: Sequence[Jogador],
        *,
        duplas: dict[str, Dupla],
        passes_jog: dict[str, int],
        pontos_para_vencer: int,
    ):
        jogadas = jogador.jogadas_validas(tabuleiro.obter_pontas())
        if not jogadas:
            raise ValueError("Jogador não possui jogadas válidas")

        estado = self._state(
            jogador,
            tabuleiro,
            jogadores,
            duplas,
            passes_jog,
            pontos_para_vencer,
        )
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

        path = r"C:\Users\ArlindoLins\Documents\Otimizando Dominó\rl_qvalues.pkl"
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
            self.q = defaultdict(float, data)
        else:
            self.q = defaultdict(float)

    def load(self, path: str) -> None:
        """Sobrescreve o arquivo de persistência e carrega seus dados."""
        path = r"C:\Users\ArlindoLins\Documents\Otimizando Dominó\rl_qvalues.pkl"
        self._load(path)
        self._file = path
