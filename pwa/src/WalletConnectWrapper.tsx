import { Web3OnboardProvider, init } from '@web3-onboard/react';
import walletConnectModule from '@web3-onboard/walletconnect';

const walletConnect = walletConnectModule({
  projectId: 'YOUR_WC_ID',
  rpcMap: { 1: 'https://ethereum-rpc.onion' } // Tor RPC
});

const onboard = init({
  wallets: [walletConnect],
  chains: [
    {
      id: '0x1',
      token: 'ETH',
      label: 'Ethereum',
      rpcUrl: 'https://ethereum-rpc.onion'
    }
  ],
  appMetadata: {
    name: 'UniaoLives',
    description: 'Plataforma de streaming com recompensas TimeChain',
    recommendedInjectedWallets: [
      { name: 'MetaMask', url: 'https://metamask.io' }
    ]
  }
});

const WalletConnectWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <Web3OnboardProvider web3Onboard={onboard}>
      {children}
    </Web3OnboardProvider>
  );
};

export default WalletConnectWrapper;