from pydantic import BaseModel, Field
from typing import Optional


class ENSResolution(BaseModel):
    """Model for ENS name resolution result"""
    ens_name: str = Field(..., description="The ENS name that was resolved")
    address: str = Field(..., description="The resolved Ethereum address")
    is_valid: bool = Field(..., description="Whether the resolution was successful")
    
    
class ReverseENSResolution(BaseModel):
    """Model for reverse ENS resolution result"""
    address: str = Field(..., description="The Ethereum address that was resolved")
    ens_name: Optional[str] = Field(None, description="The resolved ENS name, if any")
    is_valid: bool = Field(..., description="Whether the reverse resolution was successful")
