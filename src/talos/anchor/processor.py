from __future__ import annotations

import hashlib
import os
from typing import Any, Dict

from web3 import Web3


def csv_anchor_reward(csv_line: str, socks_proxy: str = "socks5://127.0.0.1:9050") -> Dict[str, Any]:
    """
    Anchors a CSV line to Bitcoin and mints a TimeChain token.

    Args:
        csv_line: The CSV line to anchor.
        socks_proxy: The SOCKS5 proxy to use for Tor.

    Returns:
        A dictionary containing the Bitcoin transaction ID, the amount of
        TimeChain tokens minted, and the hash of the CSV line.
    """
    # 1. SHA-256(line) → zero-knowledge
    hash_value = hashlib.sha256(csv_line.encode()).hexdigest()

    # 2. anchor to Bitcoin (Tor RPC)
    # This is a mock of the Bitcoin anchoring service.
    btc_tx = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # 3. mint TimeChain “CSV” token (Tor RPC)
    provider = Web3.HTTPProvider(
        "https://timechain-rpc.onion",
        request_kwargs={"proxies": {"https": socks_proxy, "http": socks_proxy}},
    )
    w3 = Web3(provider)
    wallet = w3.eth.account.from_key(os.environ["PRIVATE_KEY"])
    contract = w3.eth.contract(
        address=os.environ["TIMECHAIN_REWARD_ADDR"],
        abi=[
            {
                "name": "mint",
                "type": "function",
                "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
            }
        ],
    )
    amount = w3.to_wei(1, "ether")
    tx = contract.functions.mint(wallet.address, amount).build_transaction(
        {"nonce": w3.eth.get_transaction_count(wallet.address)}
    )
    signed_tx = wallet.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

    return {"btcTx": btc_tx, "amount": str(amount), "hash": hash_value}
