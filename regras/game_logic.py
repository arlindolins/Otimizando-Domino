from typing import List, Optional
from core.peca import Peca
from core.jogador import Jogador


def proximo_jogador_obj(jogadores: List[Jogador], atual: Jogador) -> Jogador:
    idx = jogadores.index(atual)
    return jogadores[(idx + 1) % len(jogadores)]


def determinar_tipo_batida(peca: Peca, pontas: tuple[int, int]) -> str:
    encaixa_esquerda = peca.encaixa(pontas[0])
    encaixa_direita = peca.encaixa(pontas[1])
    encaixa_ambas = encaixa_esquerda and encaixa_direita

    if peca.is_duplo() and encaixa_ambas:
        return "cruzada"
    elif not peca.is_duplo() and encaixa_ambas and pontas[0] != pontas[1]:
        return "la_e_lo"
    elif peca.is_duplo():
        return "carroca"
    elif encaixa_esquerda or encaixa_direita:
        return "simples"
    else:
        return "indefinido"


def pontuacao_por_tipo(tipo: str) -> int:
    return {
        "simples": 1,
        "carroca": 2,
        "la_e_lo": 3,
        "cruzada": 4,
        "travamento": 1
    }.get(tipo, 0)


def determinar_vencedor_travamento(jogadores: List[Jogador]) -> tuple[Optional[str], int]:
    soma_maos = {j.nome: sum(p.valor_total() for p in j.mao) for j in jogadores}
    menor_soma = min(soma_maos.values())
    vencedores = [nome for nome, soma in soma_maos.items() if soma == menor_soma]
    if len(vencedores) > 1:
        return None, 0
    return vencedores[0], 1
