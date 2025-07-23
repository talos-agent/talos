import base64
from typing import ClassVar, Dict, Type

from pydantic import BaseModel, ConfigDict, Field

from talos.services.key_management import KeyManagement
from talos.skills.base import Skill


class DecryptArgs(BaseModel):
    encrypted_data: str = Field(..., description="The base64 encoded data to decrypt.")


def get_crypto_args_schema() -> Dict[str, Type[BaseModel]]:
    return {
        "decrypt": DecryptArgs,
    }


class CryptographySkill(Skill):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: ClassVar[str] = "cryptography"
    description: ClassVar[str] = "A skill for decrypting data."

    key_management: KeyManagement = Field(default_factory=KeyManagement)
    args_schema: Dict[str, Type[BaseModel]] = Field(default_factory=get_crypto_args_schema)

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypts a base64 encoded string using the private key.
        """
        decoded_data = base64.b64decode(encrypted_data)
        return self.key_management.decrypt(decoded_data)

    def run(self, **kwargs):
        raise NotImplementedError

    def _run(self, tool_name: str, **kwargs):
        if tool_name == "decrypt":
            return self.decrypt(**kwargs)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
