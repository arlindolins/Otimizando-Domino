from core.peca import Peca
from typing import Callable, Any, List, Optional, Sequence

class Jogador:
    def __init__(self, nome: str, mao: Sequence[Peca], estrategia: Optional[Any] = None):
        self.nome = nome
        self.mao: List[Peca] = list(mao)
        self.estrategia = estrategia

    def remover_peca(self, peca: Peca):
        self.mao.remove(peca)

    def possui_jogada(self, pontas: tuple[int, int]) -> bool:
        return any(peca.encaixa(pontas[0]) or peca.encaixa(pontas[1]) for peca in self.mao)

    def jogadas_validas(self, pontas: tuple[int, int]) -> list[Peca]:
        if pontas[0] is None and pontas[1] is None:
            return self.mao.copy()
        return [peca for peca in self.mao if peca.encaixa(pontas[0]) or peca.encaixa(pontas[1])]

    def escolher_peca(self, tabuleiro, jogadores):
        """Retorna a peça escolhida para jogar de acordo com a estratégia."""
        if self.estrategia is not None:
            # Função ou objeto com método ``escolher_peca``
            if callable(self.estrategia):
                return self.estrategia(self, tabuleiro, jogadores)
            if hasattr(self.estrategia, "escolher_peca"):
                return self.estrategia.escolher_peca(self, tabuleiro, jogadores)
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

    def escolher_peca(self, tabuleiro, jogadores):
        from mcts_engine import escolher_peca_mcts, SIMULACOES_PADRAO

        sims = self.simulations if self.simulations is not None else SIMULACOES_PADRAO
        return escolher_peca_mcts(self, jogadores, tabuleiro, sims)


class CLIJogador(Jogador):
    """Jogador interativo via linha de comando."""

    def escolher_peca(self, tabuleiro, jogadores):
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

    def pode_bater_com(self, peca, L, R):
        """True se essa peça finalizaria a rodada."""
        return len(self.mao) == 1 and (peca.encaixa(L) or peca.encaixa(R))

    def tipo_batida_no_lance(self, peca, L, R):
        """
        4 = cruzada (duplo que fecha ambos)
        3 = lá-e-lô (não-duplo que fecha ambos)
        2 = carroça (duplo fecha um lado)
        1 = simples
        0 = ainda não bate
        """
        if not self.pode_bater_com(peca, L, R):
            return 0
        if peca.is_duplo():
            return 4 if L == R else 2
        return 3 if peca.encaixa(L) and peca.encaixa(R) else 1

    # baseline simples p/ adversário
    def estrategia_baseline(self, tabuleiro):
        left, right = tabuleiro.obter_pontas()
        for peca in self.mao:
            if left is None:                 # primeira jogada
                return (peca, None)
            if peca.encaixa(left):
                return (peca, "esquerda")
            if peca.encaixa(right):
                return (peca, "direita")
        return (None, None)                  # passa


