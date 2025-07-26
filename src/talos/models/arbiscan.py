from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union


class ContractSourceCode(BaseModel):
    source_code: str = Field(..., alias="SourceCode", description="The source code of the contract")
    abi: str = Field(..., alias="ABI", description="The ABI of the contract as a JSON string")
    contract_name: str = Field(..., alias="ContractName", description="The name of the contract")
    compiler_version: str = Field(..., alias="CompilerVersion", description="The compiler version used")
    optimization_used: str = Field(..., alias="OptimizationUsed", description="Whether optimization was used")
    runs: str = Field(..., alias="Runs", description="Number of optimization runs")
    constructor_arguments: str = Field(..., alias="ConstructorArguments", description="Constructor arguments")
    evm_version: str = Field(..., alias="EVMVersion", description="EVM version used")
    library: str = Field(..., alias="Library", description="Library information")
    license_type: str = Field(..., alias="LicenseType", description="License type")
    proxy: str = Field(..., alias="Proxy", description="Proxy information")
    implementation: str = Field(..., alias="Implementation", description="Implementation address if proxy")
    swarm_source: str = Field(..., alias="SwarmSource", description="Swarm source")


class ContractABI(BaseModel):
    abi: List[Dict[str, Any]] = Field(..., description="The parsed ABI as a list of dictionaries")


class ArbiScanResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    result: Union[List[ContractSourceCode], str] = Field(..., description="List of contract source code data or error message")


class ArbiScanABIResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    result: str = Field(..., description="ABI as JSON string or error message")
