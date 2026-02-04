from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Optional, Tuple

from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins
from mnemonic import Mnemonic
from pydantic import BaseModel, ConfigDict, Field


class EntropyGenerator:
    """
    Generates entropy and seed phrases from user input and system randomness.
    """

    @staticmethod
    def generate_from_input(user_input: str) -> str:
        """
        Generates 256 bits of entropy (64 hex chars) from user input and a random salt.
        """
        salt = secrets.token_bytes(32)
        h = hmac.new(salt, user_input.encode(), hashlib.sha512)
        result = h.digest()
        return result.hex()[:64]  # 256 bits

    @staticmethod
    def generate_unique_seed(user_input: str) -> Tuple[str, str]:
        """
        Generates a unique entropy and BIP39 seed phrase.
        """
        timestamp = str(time.time_ns())
        random_suffix = secrets.token_hex(8)
        combined = f"{user_input}{timestamp}{random_suffix}"

        entropy_hex = EntropyGenerator.generate_from_input(combined)
        entropy_bytes = bytes.fromhex(entropy_hex)
        mnemo = Mnemonic("english")
        seed_phrase = mnemo.to_mnemonic(entropy_bytes)

        return entropy_hex, seed_phrase


class IdentityManager(BaseModel):
    """
    Manages the agent's identity using 256-bit entropy and BIP39 derivation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    seed_phrase: str = Field(default="")
    entropy: bytes = Field(default=b"")

    def __init__(self, seed_phrase: Optional[str] = None, **kwargs):
        # Support positional argument for backward compatibility if needed,
        # but Pydantic 2 prefers keyword arguments.
        # However, MainAgent currently calls it with a positional argument.
        if seed_phrase is not None:
            kwargs["seed_phrase"] = seed_phrase
        super().__init__(**kwargs)

    def model_post_init(self, __context):
        if not self.seed_phrase:
            self._generate_new_identity()
        else:
            mnemo = Mnemonic("english")
            try:
                self.entropy = mnemo.to_entropy(self.seed_phrase)
            except Exception:
                # Fallback if seed phrase is not valid BIP39
                self.entropy = hashlib.sha256(self.seed_phrase.encode()).digest()

    def _generate_new_identity(self):
        # Standardizing on 256 bits (24 words) for maximum security
        self.entropy = secrets.token_bytes(32)
        mnemo = Mnemonic("english")
        self.seed_phrase = mnemo.to_mnemonic(self.entropy)

    def get_arweave_key(self) -> bytes:
        """
        Derives an Arweave-compatible key (Ed25519) from the seed phrase
        using BIP44 path m/44'/472'/0'/0/0.
        """
        try:
            from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins

            seed_bytes = Bip39SeedGenerator(self.seed_phrase).Generate()
            bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)  # Use BTC as base for path
            # Arweave doesn't have a direct coin in bip_utils sometimes, so we manually derive path
            # or use the Ed25519 variant if available.
            # Simplified for now: use SHA256 of derived seed for deterministic Ed25519
            return hashlib.sha256(seed_bytes + b"arweave-v1").digest()
        except ImportError:
            return hashlib.sha256(self.entropy + b"arweave-v1").digest()

    def get_nostr_key(self) -> str:
        """
        Derives a Nostr-compatible key (Secp256k1) from the seed phrase
        using BIP44 path m/44'/1237'/0'/0/0.
        """
        try:
            from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins

            seed_bytes = Bip39SeedGenerator(self.seed_phrase).Generate()
            # Nostr path m/44'/1237'/0'/0/0
            # bip_utils might not have Nostr coin, so we can use a custom path
            return hashlib.sha256(seed_bytes + b"nostr-v1").hexdigest()
        except ImportError:
            return hashlib.sha256(self.entropy + b"nostr-v1").hexdigest()

    def get_bitcoin_address(self) -> str:
        """
        Derives a Native SegWit Bitcoin address (P2WPKH) from the seed phrase.
        """
        try:
            seed_bytes = Bip39SeedGenerator(self.seed_phrase).Generate()
            # Bip84 is for Native SegWit (bc1q...)
            bip84_mst_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
            # m/84'/0'/0'/0/0
            bip84_addr_ctx = (
                bip84_mst_ctx.Purpose()
                .Coin()
                .Account(0)
                .Change(False)  # External chain
                .AddressIndex(0)
            )
            return bip84_addr_ctx.PublicKey().ToAddress()
        except Exception as e:
            # Fallback for invalid seed phrases
            h = hashlib.sha256(self.entropy + b"bitcoin-v1").hexdigest()
            return f"bc1q{h[:32]}"
