function gerarPecas() {
  return Array.from({ length: 7 }, (_, i) => 
    Array.from({ length: 7 - i }, (_, j) => [i, j + i])
  ).flat();
}

function distribuirPecas() {
  const pecas = gerarPecas();
  for (let i = pecas.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pecas[i], pecas[j]] = [pecas[j], pecas[i]];
  }
  
  const maos = {
    J1: pecas.slice(0, 6).sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    J2: pecas.slice(6, 12).sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    J3: pecas.slice(12, 18).sort((a, b) => a[0] - b[0] || a[1] - b[1]),
    J4: pecas.slice(18, 24).sort((a, b) => a[0] - b[0] || a[1] - b[1])
  };
  
  const pecasFora = pecas.slice(24);
  return [maos, pecasFora];
}

function jogadorComMaiorDuplo(maos) {
  let maiorDuplo = -1;
  let jogadorInicial = null;
  
  for (const [jogador, mao] of Object.entries(maos)) {
    for (const peca of mao) {
      if (peca[0] === peca[1] && peca[0] > maiorDuplo) {
        maiorDuplo = peca[0];
        jogadorInicial = jogador;
      }
    }
  }
  
  return [jogadorInicial, maiorDuplo];
}

function proximoJogador(jogadorAtual) {
  const ordem = ["J1", "J2", "J3", "J4"];
  const idx = ordem.indexOf(jogadorAtual);
  return ordem[(idx + 1) % 4];
}

function jogadasValidas(mao, pontas) {
  if (pontas[0] === null) return mao;
  return mao.filter(peca => 
    peca[0] === pontas[0] || peca[1] === pontas[0] || 
    peca[0] === pontas[1] || peca[1] === pontas[1]
  );
}

function jogarPeca(tabuleiro, pontas, peca) {
  if (!tabuleiro.length) {
    tabuleiro.push(peca);
    pontas[0] = peca[0];
    pontas[1] = peca[1];
    return "inicial";
  }
  
  if (peca[0] === pontas[0]) {
    tabuleiro.unshift([peca[1], peca[0]]);
    pontas[0] = peca[1];
    return "esquerda";
  } else if (peca[1] === pontas[0]) {
    tabuleiro.unshift(peca);
    pontas[0] = peca[0];
    return "esquerda";
  } else if (peca[0] === pontas[1]) {
    tabuleiro.push(peca);
    pontas[1] = peca[1];
    return "direita";
  } else if (peca[1] === pontas[1]) {
    tabuleiro.push([peca[1], peca[0]]);
    pontas[1] = peca[0];
    return "direita";
  }
}

function tipoDeBatida(pecaFinal, jogador, pontas) {
  const ehDuplo = pecaFinal[0] === pecaFinal[1];
  const encaixaEsquerda = pecaFinal[0] === pontas[0] || pecaFinal[1] === pontas[0];
  const encaixaDireita = pecaFinal[0] === pontas[1] || pecaFinal[1] === pontas[1];
  const encaixaAmbas = encaixaEsquerda && encaixaDireita;

  if (ehDuplo && encaixaAmbas) return "cruzada";
  if (!ehDuplo && encaixaAmbas && pontas[0] !== pontas[1]) return "la_e_lo";
  if (ehDuplo) return "carroca";
  if (encaixaDireita || encaixaEsquerda) return "simples";
}

function calcularPontuacaoBatida(tipoBatida) {
  const pontos = {
    simples: 1,
    carroca: 2,
    la_e_lo: 3,
    cruzada: 4
  };
  return pontos[tipoBatida] || 0;
}

function calcularPontuacaoTravamento(maos) {
  const somasMaos = Object.fromEntries(
    Object.entries(maos).map(([j, mao]) => [
      j,
      mao.reduce((sum, p) => sum + p[0] + p[1], 0)
    ])
  );
  
  const menorSoma = Math.min(...Object.values(somasMaos));
  const vencedores = Object.entries(somasMaos)
    .filter(([_, soma]) => soma === menorSoma)
    .map(([j]) => j);
  
  return vencedores.length > 1 ? [null, 0] : [vencedores[0], 1];
}

let placar = {
  "Dupla_1": 0,
  "Dupla_2": 0
};

let historicoRodadas = [];

function simularRodada() {
  const [maos, _] = distribuirPecas();
  const tabuleiro = [];
  const pontas = [null, null];
  const historico = [];
  const estados = [];
  let ordemJogada = 1;
  let [jogador, maiorDuplo] = jogadorComMaiorDuplo(maos);

  if (!jogador) {
    return { erro: "Nenhum duplo encontrado" };
  }

  let passesConsecutivos = 0;
  let vencedorRodada = null;
  let motivoFim = null;
  let tipoBatida = null;
  let pontuacaoRodada = 0;

  while (true) {
    const mao = maos[jogador];
    const jogadasDisponiveis = jogadasValidas(mao, pontas);
    const jogadas = [...jogadasDisponiveis];

    if (jogadas.length) {
      if (ordemJogada === 1) {
        const peca = [maiorDuplo, maiorDuplo];
        mao.splice(mao.findIndex(p => p[0] === maiorDuplo && p[1] === maiorDuplo), 1);
        const lado = jogarPeca(tabuleiro, pontas, peca);
        const tipo = mao.length === 0 ? "batida" : "jogada";
        historico.push({
          ordem: ordemJogada,
          jogador,
          tipo,
          peca,
          lado
        });
      } else {
        const peca = jogadas[0];
        mao.splice(mao.findIndex(p => p[0] === peca[0] && p[1] === peca[1]), 1);
        const lado = jogarPeca(tabuleiro, pontas, peca);
        const tipo = mao.length === 0 ? "batida" : "jogada";
        historico.push({
          ordem: ordemJogada,
          jogador,
          tipo,
          peca,
          lado
        });
        passesConsecutivos = 0;
        if (mao.length === 0) {
          tipoBatida = tipoDeBatida(peca, jogador, pontas);
          pontuacaoRodada = calcularPontuacaoBatida(tipoBatida);
          vencedorRodada = jogador;
          motivoFim = "batida";
        }
      }
    } else {
      historico.push({
        ordem: ordemJogada,
        jogador,
        tipo: "passe"
      });
      passesConsecutivos++;
      if (passesConsecutivos === 4) {
        [vencedorRodada, pontuacaoRodada] = calcularPontuacaoTravamento(maos);
        motivoFim = "travamento";
        tipoBatida = "travamento";
      }
    }

    estados.push({
      ordem_jogada: ordemJogada,
      jogador,
      tipo: historico[historico.length - 1].tipo,
      peca: historico[historico.length - 1].peca,
      lado: historico[historico.length - 1].lado,
      tabuleiro: [...tabuleiro],
      maos: JSON.parse(JSON.stringify(maos)),
      tipo_batida: tipoBatida,
      motivo_fim: motivoFim,
      vencedor_rodada: vencedorRodada,
      jogadas: [...historico],
      jogadas_disponiveis: jogadasDisponiveis
    });

    if (motivoFim) {
      if (vencedorRodada) {
        const dupla = ["J1", "J3"].includes(vencedorRodada) ? "Dupla_1" : "Dupla_2";
        placar[dupla] += pontuacaoRodada;
        historicoRodadas.push({
          vencedor: vencedorRodada,
          tipoBatida,
          pontos: pontuacaoRodada,
          dupla
        });
      }
      break;
    }

    ordemJogada++;
    jogador = proximoJogador(jogador);
  }

  return {
    estados,
    final: {
      tipo_batida: tipoBatida,
      motivo_fim: motivoFim,
      vencedor_rodada: vencedorRodada,
      pontuacao_rodada: pontuacaoRodada
    },
    placar,
    historicoRodadas
  };
}

module.exports = { simularRodada };