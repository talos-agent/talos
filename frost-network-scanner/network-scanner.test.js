const nock = require('nock');
const NetworkScanner = require('./network-scanner');

describe('NetworkScanner', () => {
  let scanner;

  beforeEach(() => {
    scanner = new NetworkScanner();
  });

  afterEach(() => {
    nock.cleanAll();
  });

  it('should discover a node and emit a "nodeAdded" event', async () => {
    nock('http://192.168.1.1:8000')
      .get('/api/frost/info')
      .reply(200, { id: 'node-1' });

    const nodeAddedListener = jest.fn();
    scanner.eventEmitter.on('nodeAdded', nodeAddedListener);

    await scanner.probe('192.168.1.1', 8000);

    expect(nodeAddedListener).toHaveBeenCalledWith({
      nodeId: 'node-1',
      ip: '192.168.1.1',
      port: 8000,
      data: { id: 'node-1' },
    });
  });

  it('should retry a failed probe and eventually discover a node', async () => {
    jest.setTimeout(15000);
    nock('http://192.168.1.1:8000')
      .get('/api/frost/info')
      .times(2)
      .reply(500)
      .get('/api/frost/info')
      .reply(200, { id: 'node-1' });

    const nodeAddedListener = jest.fn();
    scanner.eventEmitter.on('nodeAdded', nodeAddedListener);

    await scanner.probe('192.168.1.1', 8000);

    expect(nodeAddedListener).toHaveBeenCalledWith({
      nodeId: 'node-1',
      ip: '192.168.1.1',
      port: 8000,
      data: { id: 'node-1' },
    });
  });

  it('should emit a "nodeRemoved" event after all retries have failed', async () => {
    jest.setTimeout(15000);
    nock('http://192.168.1.1:8000')
      .get('/api/frost/info')
      .times(4)
      .reply(500);

    const nodeRemovedListener = jest.fn();
    scanner.eventEmitter.on('nodeRemoved', nodeRemovedListener);

    await scanner.probe('192.168.1.1', 8000);

    expect(nodeRemovedListener).toHaveBeenCalledWith({
      ip: '192.168.1.1',
      port: 8000,
    });
  });
});