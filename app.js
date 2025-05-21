const express = require('express');
const path = require('path');
const { simularRodada } = require('./motor_de_jogo.js');

const app = express();

app.use(express.static('static'));
app.use(express.static('templates'));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'frontend_visualizador.html'));
});

app.get('/simular', (req, res) => {
  const resultado = simularRodada();
  res.json(resultado);
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});