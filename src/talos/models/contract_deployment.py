from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ContractDeploymentRequest(BaseModel):
    bytecode: str = Field(..., description="Contract bytecode to deploy")
    salt: str = Field(..., description="Salt for CREATE2 deployment")
    chain_id: int = Field(..., description="Chain ID to deploy on")
    constructor_args: Optional[list] = Field(None, description="Constructor arguments")
    gas_limit: Optional[int] = Field(None, description="Gas limit for deployment")
    gas_price: Optional[int] = Field(None, description="Gas price in wei")


class ContractDeploymentResult(BaseModel):
    contract_address: str = Field(..., description="Deployed contract address")
    transaction_hash: str = Field(..., description="Deployment transaction hash")
    contract_signature: str = Field(..., description="Contract signature (hash)")
    chain_id: int = Field(..., description="Chain ID deployed on")
    gas_used: Optional[int] = Field(None, description="Gas used for deployment")
    was_duplicate: bool = Field(False, description="Whether this was a duplicate deployment")
