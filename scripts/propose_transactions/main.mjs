import SafeApiKit from '@safe-global/api-kit'
import Safe from '@safe-global/protocol-kit'
import { OperationType } from '@safe-global/types-kit'
import * as yaml from 'yaml'
import * as oasis from '@oasisprotocol/client'
import * as oasisRT from '@oasisprotocol/client-rt'
import xhr2 from 'xhr2';
import { readFileSync } from 'node:fs'
global.XMLHttpRequest = xhr2;

/** @type {{oci_reference: string, manifest_hash: string}} */
const OCI_AND_HASH = JSON.parse(process.argv[2])
const PROPOSER_PRIVATE_KEY = process.argv[3]

const APP_ID = 'rofl1qz8c57nvrru0rdtv7242rzwv269a87zh6c8auqr3'
// TODO: could get machine from nexus API or
const MACHINE = {
  provider: 'oasis1qrfeadn03ljm0kfx8wx0d5zf6kj79pxqvv0dukdm',
  id: '0000000000000004',
}
const SAFE_ADDRESS = '0x4b5ca97d1F45a8b589c0C161ebB258D50F756468'

console.log(OCI_AND_HASH)

async function generateTransactions() {
  const sapphireRuntimeId =
    oasis.misc.fromHex('000000000000000000000000000000000000000000000000a6d1e3ebf60dff6c') // Sapphire Testnet
  const nic = new oasis.client.NodeInternal('https://testnet.grpc.oasis.io')

  const roflmarket = new oasisRT.roflmarket.Wrapper(sapphireRuntimeId)
  const rofl = new oasisRT.rofl.Wrapper(sapphireRuntimeId)

  /** @type {any[]} */
  const enclaveIds = yaml.parse(readFileSync('rofl.yaml', 'utf8')).deployments.testnet.policy.enclaves
  const enclaves = enclaveIds.map(e => ({
    // split https://github.com/oasisprotocol/oasis-core/blob/113878af787d6c6f8da22d6b8a33f6a249180c8b/go/common/sgx/common.go#L209-L221
    mr_enclave: oasis.misc.fromBase64(e.id).slice(0, 32),
    mr_signer: oasis.misc.fromBase64(e.id).slice(32),
  }))

  const app = await rofl
    .queryApp()
    .setArgs({ id: oasisRT.rofl.fromBech32(APP_ID) })
    .query(nic)
  console.log('Found app', app)

  const machine = await roflmarket.queryInstance().setArgs({
    id: oasis.misc.fromHex(MACHINE.id),
    provider: oasis.staking.addressFromBech32(MACHINE.provider),
  }).query(nic)
  console.log('Found machine', machine)

  if (!machine.deployment?.app_id) {
    throw new Error(`Machine ${MACHINE.id} isn't running any app. Expected ${APP_ID}`)
  }
  if (oasisRT.rofl.toBech32(machine.deployment.app_id) !== APP_ID) {
    throw new Error(`Machine ${MACHINE.id} is running app ${oasisRT.rofl.toBech32(machine.deployment.app_id)}. Expected ${APP_ID}`)
  }

  const txUpdateEnclaves = rofl.callUpdate().setBody({
    id: app.id,
    admin: app.admin,
    metadata: app.metadata,
    policy: {
      ...app.policy,
      enclaves: enclaves,
    },
    secrets: app.secrets,
  }).toSubcall()

  const txUpdateMachine = roflmarket.callInstanceExecuteCmds().setBody({
    provider: oasis.staking.addressFromBech32(MACHINE.provider),
    id: oasis.misc.fromHex(MACHINE.id),
    cmds: [oasis.misc.toCBOR({
      // https://github.com/oasisprotocol/cli/blob/b6894a1bb6ea7918a9b2ba3efe30b1911388e2f6/build/rofl/scheduler/commands.go#L9-L42
      method: 'Deploy',
      args: {
        wipe_storage: false,
        deployment: {
          app_id: oasisRT.rofl.fromBech32(APP_ID),
          metadata: { 'net.oasis.deployment.orc.ref': OCI_AND_HASH.oci_reference },
          manifest_hash: oasis.misc.fromHex(OCI_AND_HASH.manifest_hash),
        },
      },
    })]
  }).toSubcall()

  const transactions = [txUpdateEnclaves, txUpdateMachine]
  console.log('Transactions to propose', transactions)
  return transactions
}

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
  safeAddress: SAFE_ADDRESS,
})

const safeTransaction = await protocolKitOwner1.createTransaction({
  transactions: (await generateTransactions()).map(tx => ({
    ...tx,
    value: tx.value ? tx.value.toString() : '0',
    operation: OperationType.Call,
  }))
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
