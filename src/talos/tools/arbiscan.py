from __future__ import annotations

import os
from typing import Any, Optional
from pydantic import BaseModel, Field

from ..models.arbiscan import ContractSourceCode, ContractABI
from ..utils.arbiscan import get_contract_source_code, get_contract_abi
from .base import SupervisedTool


class ArbiScanSourceCodeArgs(BaseModel):
    contract_address: str = Field(..., description="The contract address to get source code for")
    api_key: Optional[str] = Field(None, description="Optional API key for higher rate limits")
    chain_id: int = Field(42161, description="Chain ID (42161 for Arbitrum One, 42170 for Nova, 421614 for Sepolia)")


class ArbiScanABIArgs(BaseModel):
    contract_address: str = Field(..., description="The contract address to get ABI for")
    api_key: Optional[str] = Field(None, description="Optional API key for higher rate limits")
    chain_id: int = Field(42161, description="Chain ID (42161 for Arbitrum One, 42170 for Nova, 421614 for Sepolia)")


class ArbiScanSourceCodeTool(SupervisedTool):
    name: str = "arbiscan_source_code_tool"
    description: str = "Gets the source code of a verified smart contract from Arbiscan"
    args_schema: type[BaseModel] = ArbiScanSourceCodeArgs

    def _run_unsupervised(self, contract_address: str, api_key: Optional[str] = None, chain_id: int = 42161, **kwargs: Any) -> ContractSourceCode:
        """Gets the source code of a verified smart contract from Arbiscan"""
        api_key = api_key or os.getenv("ARBISCAN_API_KEY")
        return get_contract_source_code(contract_address=contract_address, api_key=api_key, chain_id=chain_id)


class ArbiScanABITool(SupervisedTool):
    name: str = "arbiscan_abi_tool"
    description: str = "Gets the ABI of a verified smart contract from Arbiscan"
    args_schema: type[BaseModel] = ArbiScanABIArgs

    def _run_unsupervised(self, contract_address: str, api_key: Optional[str] = None, chain_id: int = 42161, **kwargs: Any) -> ContractABI:
        """Gets the ABI of a verified smart contract from Arbiscan"""
        api_key = api_key or os.getenv("ARBISCAN_API_KEY")
        return get_contract_abi(contract_address=contract_address, api_key=api_key, chain_id=chain_id)
