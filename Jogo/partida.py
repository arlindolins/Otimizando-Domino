from core.dupla import Dupla

class Partida:
    def __init__(self, duplas: list[Dupla], pontos_para_vencer: int = 6):
        self.duplas = {d.nome: d for d in duplas}
        self.pontos_para_vencer = pontos_para_vencer
        self.rodadas = []

    def venceu(self) -> bool:
        return any(dupla.pontuacao >= self.pontos_para_vencer for dupla in self.duplas.values())

    def dupla_vencedora(self) -> str:
        return max(self.duplas.items(), key=lambda x: x[1].pontuacao)[0]
