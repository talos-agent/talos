import { ethers } from "ethers";

/**
 * verify_deployment.ts
 * Quick verification script for AIGMI Stewardship Contract.
 */
async function verifyDeployment() {
  const rpcUrl = process.env.ETHEREUM_RPC_URL;
  if (!rpcUrl) {
    console.error("ETHEREUM_RPC_URL not set");
    return;
  }

  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const address = process.env.CONTRACT_ADDRESS;
  if (!address) {
    console.error("CONTRACT_ADDRESS not set");
    return;
  }

  const code = await provider.getCode(address);
  console.log(`Contract code found: ${code !== "0x"}`);

  // ABI fragment for stewards check
  const abi = [
    "function stewards(uint256) view returns (address)",
  ];

  const contract = new ethers.Contract(address, abi, provider);

  try {
      console.log("Steward 1:", await contract.stewards(0));
      console.log("Steward 9:", await contract.stewards(8));
  } catch (e) {
      console.error("Failed to fetch stewards. Ensure 9 members are initialized.");
  }
}

if (require.main === module) {
    verifyDeployment();
}
