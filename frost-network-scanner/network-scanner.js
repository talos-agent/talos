const axios = require('axios');
const yaml = require('js-yaml');
const fs = require('fs');

class NetworkScanner {
  constructor() {
    this.config = this.loadConfig();
    this.nodes = new Map();
    this.eventEmitter = new (require('events'))();
  }

  loadConfig() {
    try {
      const configFile = fs.readFileSync('config.yaml', 'utf8');
      return yaml.load(configFile);
    } catch (error) {
      console.error('Error loading config.yaml:', error.message);
      // Return default config if file not found or invalid
      return {
        scanPorts: "8000-8100",
        healthTtl: 30000,
        maxRetries: 3,
        scanDelayMs: 100
      };
    }
  }

  async scan() {
    const [startPort, endPort] = this.config.scanPorts.split('-').map(Number);
    for (let port = startPort; port <= endPort; port++) {
      for (let i = 1; i < 255; i++) {
        const ip = `192.168.1.${i}`;
        this.probe(ip, port);
        await new Promise(resolve => setTimeout(resolve, this.config.scanDelayMs));
      }
    }
  }

  async probe(ip, port) {
    let attempts = 0;
    while (attempts < this.config.maxRetries) {
      try {
        const response = await axios.get(`http://${ip}:${port}/api/frost/info`);
        if (response.status === 200) {
          this.addNode(ip, port, response.data);
          return;
        }
      } catch (error) {
        // Log only the first error
        if (attempts === 0) {
          console.error(`Error probing ${ip}:${port}: ${error.message}`);
        }
        attempts++;
        const delay = Math.pow(2, attempts) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    this.eventEmitter.emit('nodeRemoved', { ip, port });
  }

  addNode(ip, port, data) {
    const nodeId = data.id;
    if (!this.nodes.has(nodeId)) {
      this.nodes.set(nodeId, { ip, port, data });
      this.eventEmitter.emit('nodeAdded', { nodeId, ip, port, data });
    }
  }
}

module.exports = NetworkScanner;