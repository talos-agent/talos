import SafeApiKit from '@safe-global/api-kit'
import Safe from '@safe-global/protocol-kit'
import { OperationType } from '@safe-global/types-kit'

const PROPOSER_PRIVATE_KEY = process.argv[2]

const apiKit = new SafeApiKit({
  chainId: 23295n, // Sapphire Testnet
  txServiceUrl: 'https://transaction-testnet.safe.oasis.io/api',
})

const protocolKitOwner1 = await Safe.init({
  provider: 'https://testnet.sapphire.oasis.io',
  // Generate a random ethereum private key, save it into github secrets
  // https://github.com/talos-agent/talos/settings/secrets/actions
  // and add its address as proposer to oasis safe
  // https://safe.oasis.io/settings/setup?safe=sapphire-testnet:0x4b5ca97d1F45a8b589c0C161ebB258D50F756468
  signer: PROPOSER_PRIVATE_KEY,
  safeAddress: '0x4b5ca97d1F45a8b589c0C161ebB258D50F756468',
})

const safeTransaction = await protocolKitOwner1.createTransaction({
  transactions: [{
    to: '0x0100000000000000000000000000000000000103',
    value: '0',
    data: '0x11111111',
    operation: OperationType.Call
  }]
})

const safeTxHash = await protocolKitOwner1.getTransactionHash(safeTransaction)
const signature = await protocolKitOwner1.signHash(safeTxHash)

await apiKit.proposeTransaction({
  safeAddress: await protocolKitOwner1.getAddress(),
  safeTransactionData: safeTransaction.data,
  safeTxHash,
  senderAddress: signature.signer,
  senderSignature: signature.data,
})
