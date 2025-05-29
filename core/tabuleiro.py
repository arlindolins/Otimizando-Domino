from collections import deque
from core.peca import Peca

class Tabuleiro:
    def __init__(self):
        self.pecas = deque()
        self.pontas = [None, None]

    def esta_vazio(self) -> bool:
        return not self.pecas

    def jogar(self, peca: Peca) -> str:
        if self.esta_vazio():
            self.pecas.append(peca)
            self.pontas[0], self.pontas[1] = peca.lado1, peca.lado2
            return "inicial"

        esquerda, direita = self.pontas

        if peca.lado1 == esquerda:
            self.pecas.appendleft(peca.inverter())
            self.pontas[0] = peca.lado2
            return "esquerda"
        elif peca.lado2 == esquerda:
            self.pecas.appendleft(peca)
            self.pontas[0] = peca.lado1
            return "esquerda"
        elif peca.lado1 == direita:
            self.pecas.append(peca)
            self.pontas[1] = peca.lado2
            return "direita"
        elif peca.lado2 == direita:
            self.pecas.append(peca.inverter())
            self.pontas[1] = peca.lado1
            return "direita"
        else:
            raise ValueError("Jogada inválida")

    def obter_pontas(self) -> tuple[int, int]:
        return tuple(self.pontas)
