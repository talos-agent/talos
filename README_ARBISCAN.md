# Arbiscan Service

This service provides integration with the Etherscan V2 API to retrieve verified smart contract source code and ABI data from Arbitrum networks.

## Features

- **Contract Source Code Retrieval**: Get the complete source code of verified smart contracts
- **Contract ABI Retrieval**: Get the Application Binary Interface (ABI) of verified contracts
- **Multi-Network Support**: Supports Arbitrum One (42161), Arbitrum Nova (42170), and Arbitrum Sepolia Testnet (421614)
- **Error Handling**: Graceful handling of API errors and unverified contracts
- **Supervised Tool Integration**: Integrated with Talos hypervisor system for controlled access

## Usage

### Direct API Usage

```python
from talos.utils.arbiscan import get_contract_source_code, get_contract_abi

# Get contract source code
contract_address = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
source_code = get_contract_source_code(
    contract_address=contract_address,
    api_key="your_etherscan_api_key",  # Required
    chain_id=42161  # Arbitrum One
)

print(f"Contract: {source_code.contract_name}")
print(f"Compiler: {source_code.compiler_version}")
print(f"Source: {source_code.source_code}")

# Get contract ABI
abi = get_contract_abi(
    contract_address=contract_address,
    api_key="your_etherscan_api_key",  # Required
    chain_id=42161
)

print(f"ABI functions: {len(abi.abi)}")
```

### Tool Usage (via Talos Agent)

The service is automatically registered as supervised tools in the main agent:

- `arbiscan_source_code_tool`: Retrieves contract source code
- `arbiscan_abi_tool`: Retrieves contract ABI

## API Key Requirement

**Important**: An Etherscan API key is required for all requests. To get an API key:

1. Create an account at [https://etherscan.io/](https://etherscan.io/)
2. Go to your Account Dashboard
3. Click on the "API-KEYs" tab
4. Create a new API key for your project

Each Etherscan account can create up to 3 API keys.

## Supported Networks

| Network | Chain ID | Description |
|---------|----------|-------------|
| Arbitrum One Mainnet | 42161 | Main Arbitrum network |
| Arbitrum Nova Mainnet | 42170 | Arbitrum Nova network |
| Arbitrum Sepolia Testnet | 421614 | Arbitrum testnet |

## Error Handling

The service handles various error conditions:

- **Missing API Key**: Returns clear error message about API key requirement
- **Invalid Contract Address**: Returns error for non-existent contracts
- **Unverified Contracts**: Returns error for contracts that haven't been verified
- **Network Issues**: Handles HTTP request failures gracefully

## Data Models

### ContractSourceCode
Contains complete contract information including:
- Source code
- ABI (as JSON string)
- Contract name
- Compiler version and settings
- Optimization details
- Constructor arguments
- Proxy information (if applicable)

### ContractABI
Contains parsed ABI data:
- ABI as list of function/event definitions
- Ready for use with web3 libraries

## Testing

Run the test script to verify the service:

```bash
python test_arbiscan.py
```

Note: Without an API key, the test will demonstrate proper error handling.
