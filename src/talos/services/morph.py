from __future__ import annotations

from web3 import Web3


class MorphService:
    """
    A service for interacting with the Morph network.
    """

    def __init__(self, provider_url: str):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))

    def get_latest_block_number(self) -> int:
        """
        Gets the latest block number from the Morph network.
        """
        return self.w3.eth.block_number

    def send_transaction(self, from_address: str, to_address: str, private_key: str, value: int) -> str:
        """
        Sends a simple transaction on the Morph network.
        """
        checksum_address = Web3.to_checksum_address(from_address)
        nonce = self.w3.eth.get_transaction_count(checksum_address)
        tx = {
            "nonce": nonce,
            "to": to_address,
            "value": value,
            "gas": 2000000,
            "gasPrice": self.w3.eth.gas_price,
        }
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
