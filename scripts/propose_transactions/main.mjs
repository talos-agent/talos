import SafeApiKit from "@safe-global/api-kit";
import Safe from "@safe-global/protocol-kit";
import { OperationType } from "@safe-global/types-kit";
import * as yaml from "yaml";
import * as oasis from "@oasisprotocol/client";
import * as oasisRT from "@oasisprotocol/client-rt";
import xhr2 from "xhr2";
import { readFileSync } from "node:fs";
global.XMLHttpRequest = xhr2;

/** @type {{oci_reference: string, manifest_hash: string}} */
const DEPLOYMENT_INFO = JSON.parse(process.env["DEPLOYMENT_INFO"]);
const DEPLOYMENT = process.env["DEPLOYMENT"];
const PROPOSER_PRIVATE_KEY = process.env["PROPOSER_PRIVATE_KEY"];
const SAFE_ADDRESS = process.env["SAFE_ADDRESS"];

// Parse and load the ROFL app manifest.
const roflAppManifest = yaml.parse(readFileSync("rofl.yaml", "utf8"));
const roflAppDeployment = roflAppManifest.deployments[DEPLOYMENT];
const roflAppId = roflAppDeployment.app_id;
const roflMachine = roflAppDeployment.machines["default"];

const networks = {
  // Sapphire Mainnet.
  mainnet: {
    runtimeId:
      "000000000000000000000000000000000000000000000000f80306c9858e7279",
    chainId: 23294n,
    grpcApi: "https://grpc.oasis.io",
    web3Api: "https://sapphire.oasis.io",
    safeApi: "https://transaction.safe.oasis.io/api",
  },
  // Sapphire Testnet.
  testnet: {
    runtimeId:
      "000000000000000000000000000000000000000000000000a6d1e3ebf60dff6c",
    chainId: 23295n,
    grpcApi: "https://testnet.grpc.oasis.io",
    web3Api: "https://testnet.sapphire.oasis.io",
    safeApi: "https://transaction-testnet.safe.oasis.io/api",
  },
};
const networkInfo = networks[roflAppDeployment.network];

console.log("Going to deploy", DEPLOYMENT_INFO);

async function generateTransactions() {
  const sapphireRuntimeId = oasis.misc.fromHex(networkInfo.runtimeId);
  const nic = new oasis.client.NodeInternal(networkInfo.grpcApi);

  const roflmarket = new oasisRT.roflmarket.Wrapper(sapphireRuntimeId);
  const rofl = new oasisRT.rofl.Wrapper(sapphireRuntimeId);

  /** @type {any[]} */
  const enclaveIds = roflAppDeployment.policy.enclaves;
  const enclaves = enclaveIds.map((e) => ({
    // split https://github.com/oasisprotocol/oasis-core/blob/113878af787d6c6f8da22d6b8a33f6a249180c8b/go/common/sgx/common.go#L209-L221
    mr_enclave: oasis.misc.fromBase64(e.id).slice(0, 32),
    mr_signer: oasis.misc.fromBase64(e.id).slice(32),
  }));

  const app = await rofl
    .queryApp()
    .setArgs({ id: oasisRT.rofl.fromBech32(roflAppId) })
    .query(nic);
  console.log("Found app", app);

  const machine = await roflmarket
    .queryInstance()
    .setArgs({
      id: oasis.misc.fromHex(roflMachine.id),
      provider: oasis.staking.addressFromBech32(roflMachine.provider),
    })
    .query(nic);
  console.log("Found machine", machine);

  if (!machine.deployment?.app_id) {
    throw new Error(
      `Machine ${roflMachine.id} isn't running any app. Expected ${roflAppId}`,
    );
  }
  if (oasisRT.rofl.toBech32(machine.deployment.app_id) !== roflAppId) {
    throw new Error(
      `Machine ${roflMachine.id} is running app ${oasisRT.rofl.toBech32(machine.deployment.app_id)}. Expected ${roflAppId}`,
    );
  }

  const txUpdateEnclaves = rofl
    .callUpdate()
    .setBody({
      id: app.id,
      admin: app.admin,
      metadata: app.metadata,
      policy: {
        ...app.policy,
        enclaves: enclaves,
      },
      secrets: app.secrets,
    })
    .toSubcall();

  const txUpdateMachine = roflmarket
    .callInstanceExecuteCmds()
    .setBody({
      provider: oasis.staking.addressFromBech32(roflMachine.provider),
      id: oasis.misc.fromHex(roflMachine.id),
      cmds: [
        oasis.misc.toCBOR({
          // https://github.com/oasisprotocol/cli/blob/b6894a1bb6ea7918a9b2ba3efe30b1911388e2f6/build/rofl/scheduler/commands.go#L9-L42
          method: "Deploy",
          args: {
            wipe_storage: false,
            deployment: {
              app_id: oasisRT.rofl.fromBech32(roflAppId),
              metadata: {
                "net.oasis.deployment.orc.ref": DEPLOYMENT_INFO.oci_reference,
              },
              manifest_hash: oasis.misc.fromHex(DEPLOYMENT_INFO.manifest_hash),
            },
          },
        }),
      ],
    })
    .toSubcall();

  const transactions = [txUpdateEnclaves, txUpdateMachine];
  console.log("Transactions to propose", transactions);
  return transactions;
}

const safeClient = new SafeApiKit({
  chainId: networkInfo.chainId,
  txServiceUrl: networkInfo.safeApi,
});

const safeProposer = await Safe.init({
  provider: networkInfo.web3Api,
  // Generate a random ethereum private key, save it into github secrets
  // https://github.com/talos-agent/talos/settings/secrets/actions
  // and add its address as proposer to oasis safe
  // https://safe.oasis.io/settings/setup?safe=sapphire-testnet:0x4b5ca97d1F45a8b589c0C161ebB258D50F756468
  signer: PROPOSER_PRIVATE_KEY,
  safeAddress: SAFE_ADDRESS,
});

const safeTransaction = await safeProposer.createTransaction({
  transactions: (await generateTransactions()).map((tx) => ({
    ...tx,
    value: tx.value ? tx.value.toString() : "0",
    operation: OperationType.Call,
  })),
});

const safeTxHash = await safeProposer.getTransactionHash(safeTransaction);
const signature = await safeProposer.signHash(safeTxHash);

await safeClient.proposeTransaction({
  safeAddress: await safeProposer.getAddress(),
  safeTransactionData: safeTransaction.data,
  safeTxHash,
  senderAddress: signature.signer,
  senderSignature: signature.data,
});

console.log("Proposed transaction hash", safeTxHash);
