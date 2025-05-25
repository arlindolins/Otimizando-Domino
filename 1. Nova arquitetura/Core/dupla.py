class Dupla:
    def __init__(self, nome: str, jogadores: list[str]):
        self.nome = nome
        self.jogadores = jogadores
        self.pontuacao = 0

    def adicionar_pontos(self, pontos: int):
        self.pontuacao += pontos

    def contem_jogador(self, jogador: str) -> bool:
        return jogador in self.jogadores
