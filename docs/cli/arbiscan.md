# Arbiscan CLI

The Arbiscan CLI module provides commands for retrieving smart contract source code from Arbitrum blockchain networks.

## Commands

### `get-source-code` - Retrieve Contract Source Code

Gets the source code of a verified smart contract from Arbiscan.

```bash
uv run talos arbiscan get-source-code <contract_address> [options]
```

**Arguments:**
- `contract_address`: The contract address to get source code for (required)

**Options:**
- `--api-key, -k`: Optional API key for higher rate limits
- `--chain-id, -c`: Chain ID (default: 42161 for Arbitrum One)
- `--format, -f`: Output format - 'formatted', 'json', or 'source-only' (default: 'formatted')

## Supported Networks

| Chain ID | Network | Description |
|----------|---------|-------------|
| 42161 | Arbitrum One | Main Arbitrum network |
| 42170 | Arbitrum Nova | Arbitrum Nova network |
| 421614 | Arbitrum Sepolia | Arbitrum testnet |

## Usage Examples

### Basic Usage

```bash
# Get source code for a contract on Arbitrum One
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678

# Get source code with API key for higher rate limits
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678 --api-key your_api_key
```

### Different Networks

```bash
# Get source code from Arbitrum Nova
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678 --chain-id 42170

# Get source code from Arbitrum Sepolia testnet
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678 --chain-id 421614
```

### Output Formats

```bash
# Formatted output (default) - human-readable with contract details
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678 --format formatted

# JSON output - structured data format
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678 --format json

# Source code only - just the contract source code
uv run talos arbiscan get-source-code 0x1234567890abcdef1234567890abcdef12345678 --format source-only
```

## Output Information

### Formatted Output

The formatted output includes:
- **Contract Name**: Name of the smart contract
- **Compiler Version**: Solidity compiler version used
- **Optimization Used**: Whether compiler optimization was enabled
- **Optimization Runs**: Number of optimization runs (if enabled)
- **License Type**: Contract license information
- **Proxy Implementation**: Implementation address (for proxy contracts)
- **Source Code**: Complete contract source code

### JSON Output

The JSON output provides structured data with all contract information in a machine-readable format.

### Source-Only Output

Returns only the contract source code without additional metadata.

## API Key Setup

### Environment Variable

Set your Arbiscan API key as an environment variable:

```bash
export ARBISCAN_API_KEY=your_api_key_here
```

### Command Line Option

Alternatively, provide the API key directly:

```bash
uv run talos arbiscan get-source-code 0x1234... --api-key your_api_key_here
```

### Getting an API Key

1. Visit [https://arbiscan.io/apis](https://arbiscan.io/apis)
2. Create a free account
3. Generate an API key
4. Use the key for higher rate limits and better reliability

## Rate Limits

- **Without API Key**: Limited requests per minute
- **With API Key**: Higher rate limits and better reliability
- **Free Tier**: Sufficient for most use cases
- **Paid Tiers**: Available for high-volume usage

## Error Handling

The command includes comprehensive error handling for:

### API Errors
- Missing or invalid API key
- Rate limit exceeded
- Invalid contract address
- Contract not verified
- Network connectivity issues

### Input Validation
- Invalid contract address format
- Unsupported chain ID
- Invalid output format

### Example Error Messages

```bash
# Missing API key error
Error: Arbiscan API key is required to get contract source code.
Please provide an API key using the --api-key option.
You can get a free API key from https://arbiscan.io/apis

# Invalid contract address
Error: Invalid contract address format

# Contract not verified
Error: Contract source code not verified on Arbiscan
```

## Integration

The Arbiscan CLI integrates with:
- Smart contract analysis workflows
- Security audit processes
- Development and debugging tools
- Automated contract verification systems

## Use Cases

- **Security Analysis**: Review contract source code for vulnerabilities
- **Development**: Study implementation patterns and best practices
- **Auditing**: Verify contract functionality and security
- **Research**: Analyze DeFi protocols and smart contract architectures
- **Integration**: Retrieve contract ABIs and interfaces for development
