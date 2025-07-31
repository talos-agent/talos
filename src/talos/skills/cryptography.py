import base64
from typing import ClassVar, Dict, Type

from pydantic import BaseModel, ConfigDict, Field

from talos.services.key_management import KeyManagement
from talos.skills.base import Skill


class CryptoArgs(BaseModel):
    data: str = Field(..., description="The data to encrypt or decrypt.")
    decrypt: bool = Field(False, description="Whether to decrypt or encrypt.")
    public_key: str | None = Field(None, description="The base64 encoded public key to use for encryption.")


def get_crypto_args_schema() -> Dict[str, Type[BaseModel]]:
    return {
        "run": CryptoArgs,
    }


class CryptographySkill(Skill):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: ClassVar[str] = "cryptography"
    description: ClassVar[str] = "A skill for encrypting and decrypting data."

    key_management: KeyManagement = Field(default_factory=KeyManagement)
    args_schema: Dict[str, Type[BaseModel]] = Field(default_factory=get_crypto_args_schema)

    def encrypt(self, data: str, public_key: str) -> str:
        """
        Encrypts data using the public key and returns it as a base64 encoded string.
        """
        from talos.utils.validation import sanitize_user_input
        
        if not data or not public_key:
            raise ValueError("Data and public key are required for encryption")
        
        data = sanitize_user_input(data, max_length=10000)
        
        try:
            decoded_public_key = base64.b64decode(public_key, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid base64 public key: {e}")
        
        if len(decoded_public_key) != 32:
            raise ValueError("Invalid public key length")
        
        encrypted_data = self.key_management.encrypt(data, decoded_public_key)
        return base64.b64encode(encrypted_data).decode()

    def decrypt(self, data: str) -> str:
        """
        Decrypts a base64 encoded string using the private key.
        """
        if not data:
            raise ValueError("Data is required for decryption")
        
        try:
            decoded_data = base64.b64decode(data, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid base64 encrypted data: {e}")
        
        return self.key_management.decrypt(decoded_data)

    def run(self, **kwargs) -> str:
        if "decrypt" in kwargs and kwargs["decrypt"]:
            return self.decrypt(kwargs["data"])
        else:
            if "public_key" not in kwargs:
                raise ValueError("Public key is required for encryption.")
            return self.encrypt(kwargs["data"], kwargs["public_key"])
