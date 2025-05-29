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

