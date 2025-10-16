import React from 'react';
import ReactDOM from 'react-dom';
import WalletConnectWrapper from './WalletConnectWrapper';

const App = () => {
  return (
    <WalletConnectWrapper>
      <h1>UniaoLives</h1>
      <p>Plataforma de streaming com recompensas TimeChain</p>
    </WalletConnectWrapper>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));