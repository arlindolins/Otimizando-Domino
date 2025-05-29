from core.jogador import Jogador
from core.tabuleiro import Tabuleiro

class Rodada:
    def __init__(self, jogadores: list[Jogador], jogador_inicial: str):
        self.jogadores = {j.nome: j for j in jogadores}
        self.jogador_atual = jogador_inicial
        self.tabuleiro = Tabuleiro()
        self.historico = []
        self.estados = []
        self.ordem_jogada = 1
        self.vencedor = None
        self.tipo_batida = None
        self.motivo_fim = None
