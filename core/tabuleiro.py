from collections import deque
from core.peca import Peca

class Tabuleiro:
    """Representa o tabuleiro de dominó."""

    def __init__(self):
        self.pecas = deque()
        self.pontas = [None, None]
        self._passes_consecutivos = 0

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
        
    def projetar_pontas(self, peca, lado):
        """
        Retorna (left, right) caso 'peca' fosse jogada em 'lado'.
        Não altera o estado real do tabuleiro.
        """
        left, right = self.pontas
        if lado is None:           # primeira jogada
            return (peca.lado1, peca.lado2)
        if lado == "esquerda":
            new_left = peca.lado1 if peca.lado2 == left else peca.lado2
            return (new_left, right)
        else:
            new_right = peca.lado2 if peca.lado1 == right else peca.lado1
            return (left, new_right)


    def obter_pontas(self) -> tuple[int, int]:
        return tuple(self.pontas)

    # ------------------------------------------------------------------
    # Novos utilitários
    # ------------------------------------------------------------------
    def resetar_passes(self) -> None:
        self._passes_consecutivos = 0

    def registrar_passe(self) -> None:
        self._passes_consecutivos += 1

    @property
    def passes_consecutivos(self) -> int:
        return self._passes_consecutivos

    def restantes_por_valor(self) -> list[int]:
        """Quantidade de peças restantes para cada valor (0‑6)."""
        restantes = [7] * 7
        for p in self.pecas:
            restantes[p.lado1] -= 1
            if p.lado2 != p.lado1:
                restantes[p.lado2] -= 1
        return restantes

    def contagem_por_valor(self) -> list[int]:
        """Contagem já jogada para cada valor (0‑6)."""
        usados = [0] * 7
        for p in self.pecas:
            usados[p.lado1] += 1
            if p.lado2 != p.lado1:
                usados[p.lado2] += 1
        return usados
