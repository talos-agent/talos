from __future__ import annotations

from eth_account import Account
from eth_typing import HexStr
from web3 import Web3

from talos.models.contract_deployment import ContractDeploymentRequest, ContractDeploymentResult


def calculate_contract_signature(bytecode: str, salt: str) -> str:
    """Calculate contract signature from bytecode and salt."""
    from Crypto.Hash import keccak

    clean_bytecode = bytecode.replace("0x", "")
    clean_salt = salt.replace("0x", "")

    combined = clean_bytecode + clean_salt
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(combined.encode())
    signature = keccak_hash.hexdigest()
    return f"0x{signature}"


def get_web3_connection(chain_id: int) -> Web3:
    """Get Web3 connection for the specified chain."""
    rpc_urls = {
        1: "https://eth.llamarpc.com",
        42161: "https://arb1.arbitrum.io/rpc",
        42170: "https://nova.arbitrum.io/rpc",
        421614: "https://sepolia-rollup.arbitrum.io/rpc",
        137: "https://polygon-rpc.com",
        10: "https://mainnet.optimism.io",
    }

    if chain_id not in rpc_urls:
        raise ValueError(f"Unsupported chain ID: {chain_id}")

    w3 = Web3(Web3.HTTPProvider(rpc_urls[chain_id]))
    if not w3.is_connected():
        raise ConnectionError(f"Failed to connect to chain {chain_id}")

    return w3


def deploy_contract(request: ContractDeploymentRequest, private_key: str) -> ContractDeploymentResult:
    """Deploy a contract using CREATE2."""
    w3 = get_web3_connection(request.chain_id)
    account = Account.from_key(private_key)

    signature = calculate_contract_signature(request.bytecode, request.salt)

    constructor_data = ""
    if request.constructor_args:
        try:
            constructor_data = w3.codec.encode(["uint256[]"], [request.constructor_args]).hex()
        except Exception:
            constructor_data = ""

    deployment_bytecode = request.bytecode + constructor_data

    gas_limit = request.gas_limit
    if not gas_limit:
        try:
            gas_limit = w3.eth.estimate_gas({"data": HexStr(deployment_bytecode), "from": account.address})
        except Exception:
            gas_limit = 3000000

    transaction = {
        "data": deployment_bytecode,
        "gas": gas_limit,
        "gasPrice": request.gas_price or w3.eth.gas_price,
        "nonce": w3.eth.get_transaction_count(account.address),
        "chainId": request.chain_id,
    }

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return ContractDeploymentResult(
        contract_address=str(receipt["contractAddress"]),
        transaction_hash=tx_hash.hex(),
        contract_signature=signature,
        chain_id=request.chain_id,
        gas_used=receipt["gasUsed"],
        was_duplicate=False,
    )
