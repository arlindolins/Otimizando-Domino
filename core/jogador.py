from core.peca import Peca
from typing import Callable, Any, List, Optional, Sequence, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from rl_engine import RLDominoStrategy


class Jogador:
    """Entidade básica de jogador."""

    def __init__(
        self, nome: str, mao: Sequence[Peca], estrategia: Optional[Any] = None
    ):
        self.nome = nome
        self.mao: List[Peca] = list(mao)
        self.estrategia = estrategia
        self._ausentes: set[int] = set()

    def remover_peca(self, peca: Peca):
        self.mao.remove(peca)

    def possui_jogada(self, pontas: tuple[int, int]) -> bool:
        return any(
            peca.encaixa(pontas[0]) or peca.encaixa(pontas[1]) for peca in self.mao
        )

    def jogadas_validas(self, pontas: tuple[int, int]) -> list[Peca]:
        if pontas[0] is None and pontas[1] is None:
            return self.mao.copy()
        return [
            peca
            for peca in self.mao
            if peca.encaixa(pontas[0]) or peca.encaixa(pontas[1])
        ]

    def registrar_passe(self, pontas: tuple[int, int]) -> None:
        """Guarda valores que comprovadamente não estão na mão."""
        self._ausentes.update({pontas[0], pontas[1]})

    def valores_comprovadamente_ausentes(self) -> set[int]:
        return set(self._ausentes)

    def escolher_peca(
        self,
        tabuleiro,
        jogadores,
        *,
        duplas=None,
        passes_jog=None,
        pontos_para_vencer: int | None = None,
    ):
        """Retorna a peça escolhida de acordo com a estratégia."""
        if self.estrategia is not None:
            if callable(self.estrategia):
                return self.estrategia(
                    self,
                    tabuleiro,
                    jogadores,
                    duplas=duplas,
                    passes_jog=passes_jog,
                    pontos_para_vencer=pontos_para_vencer,
                )
            if hasattr(self.estrategia, "escolher_peca"):
                return self.estrategia.escolher_peca(
                    self,
                    tabuleiro,
                    jogadores,
                    duplas=duplas,
                    passes_jog=passes_jog,
                    pontos_para_vencer=pontos_para_vencer,
                )
            raise TypeError("Estratégia inválida")

        jogadas = self.jogadas_validas(tabuleiro.obter_pontas())
        if not jogadas:
            raise ValueError("Jogador não possui jogadas válidas")
        return jogadas[0]


class MCTSJogador(Jogador):
    """Jogador que utiliza a estratégia Monte Carlo para decidir a jogada."""

    def __init__(self, nome: str, mao: Sequence[Peca], simulations: int = None):
        super().__init__(nome, mao)
        self.simulations = simulations

    def escolher_peca(self, tabuleiro, jogadores, **_):
        from mcts_engine import escolher_peca_mcts, SIMULACOES_PADRAO

        sims = self.simulations if self.simulations is not None else SIMULACOES_PADRAO
        return escolher_peca_mcts(self, jogadores, tabuleiro, sims)


class CLIJogador(Jogador):
    """Jogador interativo via linha de comando."""

    def escolher_peca(self, tabuleiro, jogadores, **_):
        jogadas = self.jogadas_validas(tabuleiro.obter_pontas())
        if not jogadas:
            raise ValueError("Jogador não possui jogadas válidas")

        print(f"Jogador {self.nome} - escolha a peça para jogar:")
        for idx, p in enumerate(jogadas):
            print(f" {idx}: ({p.lado1}, {p.lado2})")
        escolha = None
        while escolha is None:
            try:
                escolha = int(input("Digite o índice da peça: "))
                if escolha < 0 or escolha >= len(jogadas):
                    print("Índice inválido.")
                    escolha = None
            except ValueError:
                print("Entrada inválida.")
        return jogadas[escolha]


def escolher_peca_ga(jogador: "Jogador", tabuleiro, jogadores, pesos: Sequence[float]):
    """Escolhe a peça com base em uma heurística ponderada.

    Os pesos devem ser uma sequência numérica. Apenas três características são
    consideradas:

    - ``pesos[0]`` → soma dos valores da peça (pip sum)
    - ``pesos[1]`` → bônus se a peça for dupla
    - ``pesos[2]`` → bônus se a peça encaixa em ambas as pontas
    """

    jogadas = jogador.jogadas_validas(tabuleiro.obter_pontas())
    if not jogadas:
        raise ValueError("Jogador não possui jogadas válidas")

    pontas = tabuleiro.obter_pontas()

    def _avaliar(peca: Peca) -> float:
        score = 0.0
        if len(pesos) > 0:
            score += pesos[0] * peca.valor_total()
        if len(pesos) > 1:
            score += pesos[1] * (1 if peca.is_duplo() else 0)
        if len(pesos) > 2:
            encaixa_ambas = peca.encaixa(pontas[0]) and peca.encaixa(pontas[1])
            score += pesos[2] * (1 if encaixa_ambas else 0)
        return score

    return max(jogadas, key=_avaliar)


class GAJogador(Jogador):
    """Jogador que utiliza pesos de uma heurística estilo GA."""

    def __init__(self, nome: str, mao: Sequence[Peca], pesos: Sequence[float]):
        """Inicializa o jogador com uma lista de ``8`` pesos.

        Os valores devem seguir a ordem definida em ``ga_domino.py``:

        ``w0``‥``w7`` → ``opp_can``, ``partner_can``, ``opp_unknown``,
        ``partner_unknown``, ``own_future``, ``pip_sum``, ``can_finish_type`` e
        ``enemy_close_to_game``.
        """
        if len(pesos) != 8:
            raise ValueError("esperados 8 pesos para a estratégia GA")

        super().__init__(nome, mao)
        self.pesos = list(pesos)

        (
            self.w0,
            self.w1,
            self.w2,
            self.w3,
            self.w4,
            self.w5,
            self.w6,
            self.w7,
        ) = self.pesos

    def escolher_peca(self, tabuleiro, jogadores, **_):
        return escolher_peca_ga(self, tabuleiro, jogadores, self.pesos)


class RLJogador(Jogador):
    """Jogador que utiliza a estratégia de Q-learning persistente."""

    def __init__(
        self,
        nome: str,
        mao: Sequence[Peca],
        *,
        arquivo: str = "rl_qvalues.pkl",
        alpha: float = 0.1,
        epsilon: float = 0.1,
    ):
        from rl_engine import RLDominoStrategy

        strategy = RLDominoStrategy(
            alpha=alpha,
            epsilon=epsilon,
            persistence_file=arquivo,
        )
        super().__init__(nome, mao, estrategia=strategy)

    def salvar(self) -> None:
        """Persiste a tabela Q em disco."""
        estrategia = getattr(self, "estrategia", None)
        if hasattr(estrategia, "save"):
            estrategia.save()
