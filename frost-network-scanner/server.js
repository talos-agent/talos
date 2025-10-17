const express = require('express');
const oasGenerator = require('express-oas-generator');
const NetworkScanner = require('./network-scanner');

const app = express();
oasGenerator.init(app, {});

const scanner = new NetworkScanner();

app.get('/api/frost/info', (req, res) => {
  res.json({ message: 'FROST node information' });
});

app.post('/api/frost/handshake', (req, res) => {
  res.json({ message: 'Handshake successful' });
});

app.get('/api/frost/status', (req, res) => {
  res.json({ nodes: Array.from(scanner.nodes.values()) });
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});