from dataclasses import dataclass

@dataclass(frozen=True)
class Peca:
    lado1: int
    lado2: int

    def is_duplo(self) -> bool:
        return self.lado1 == self.lado2

    def valor_total(self) -> int:
        return self.lado1 + self.lado2

    def inverter(self) -> "Peca":
        return Peca(self.lado2, self.lado1)

    def encaixa(self, valor: int) -> bool:
        return self.lado1 == valor or self.lado2 == valor
