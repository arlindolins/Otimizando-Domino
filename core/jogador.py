from core.peca import Peca

class Jogador:
    def __init__(self, nome: str, mao: list[Peca]):
        self.nome = nome
        self.mao = mao

    def remover_peca(self, peca: Peca):
        self.mao.remove(peca)

    def possui_jogada(self, pontas: tuple[int, int]) -> bool:
        return any(peca.encaixa(pontas[0]) or peca.encaixa(pontas[1]) for peca in self.mao)

    def jogadas_validas(self, pontas: tuple[int, int]) -> list[Peca]:
        if pontas[0] is None and pontas[1] is None:
            return self.mao.copy()
        return [peca for peca in self.mao if peca.encaixa(pontas[0]) or peca.encaixa(pontas[1])]

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


