# CLI Overview

The Talos CLI is the main entry point for interacting with the Talos agent. It provides both interactive and non-interactive modes for different use cases.

## Installation

The CLI is installed as part of the `talos` package. After installation, you can run:

```bash
uv run talos
```

## Usage Modes

### Interactive Mode

To enter interactive mode, run `talos` without any arguments:

```bash
uv run talos
```

This starts a continuous conversation where you can:
- Ask questions about protocol management
- Request analysis and recommendations
- Execute commands and workflows
- Get help and guidance

Example session:
```
>> What are your main capabilities?
>> Analyze the sentiment around "DeFi protocols" on Twitter
>> Help me evaluate a governance proposal
>> exit
```

Type `exit` to quit the interactive session.

### Non-Interactive Mode

In non-interactive mode, you can run a single query and the agent will exit:

```bash
uv run talos "your query here"
```

Examples:
```bash
uv run talos "What is the current market sentiment?"
uv run talos "Analyze the latest governance proposal"
uv run talos "Check GitHub PRs for security issues"
```

### Daemon Mode

Run Talos continuously for scheduled operations and automated tasks:

```bash
uv run talos daemon
```

The daemon mode:
- Executes scheduled jobs automatically
- Monitors for new proposals and PRs
- Performs continuous market analysis
- Handles automated responses and alerts
- Can be gracefully shutdown with SIGTERM or SIGINT

## Command Structure

The Talos CLI uses a hierarchical command structure:

```
talos [global-options] <command> [command-options] [arguments]
```

### Global Options

- `--help, -h` - Show help information
- `--version` - Show version information
- `--config` - Specify configuration file path
- `--verbose, -v` - Enable verbose logging

### Available Commands

| Command | Description |
|---------|-------------|
| `twitter` | Twitter-related operations and sentiment analysis |
| `github` | GitHub repository management and PR reviews |
| `proposals` | Governance proposal evaluation |
| `memory` | Memory management and search operations |
| `arbiscan` | Arbitrum blockchain contract source code retrieval |
| `generate-keys` | Generate RSA key pairs for encryption |
| `get-public-key` | Retrieve the current public key |
| `encrypt` | Encrypt data using public key |
| `decrypt` | Decrypt data using private key |
| `daemon` | Run in continuous daemon mode |
| `cleanup-users` | Clean up temporary users and conversation data |
| `db-stats` | Show database statistics |

## Environment Variables

### Required Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export PINATA_API_KEY="your-pinata-api-key"
export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
```

### Optional Variables

```bash
export GITHUB_API_TOKEN="your-github-token"        # For GitHub operations
export TWITTER_BEARER_TOKEN="your-twitter-token"   # For Twitter analysis
export GITHUB_REPO="owner/repo"                    # Default repository
export ARBISCAN_API_KEY="your-arbiscan-key"        # For higher rate limits on Arbitrum data
```

## Configuration

### Configuration File

Talos can be configured using a YAML configuration file:

```yaml
# talos.yml
api_keys:
  openai: "${OPENAI_API_KEY}"
  github: "${GITHUB_API_TOKEN}"
  twitter: "${TWITTER_BEARER_TOKEN}"

defaults:
  github_repo: "owner/repo"
  twitter_query_limit: 100
  
logging:
  level: "INFO"
  file: "talos.log"

hypervisor:
  approval_timeout: 30
  max_pending_actions: 100
```

Specify the configuration file:
```bash
uv run talos --config talos.yml
```

### Environment File

Create a `.env` file for convenience:

```bash
# .env
OPENAI_API_KEY=your-openai-api-key
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_API_KEY=your-pinata-secret-api-key
GITHUB_API_TOKEN=your-github-token
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
GITHUB_REPO=owner/repo
```

## Error Handling

The CLI includes comprehensive error handling for:

- **Missing API Keys** - Clear messages about required environment variables
- **Network Issues** - Retry logic and timeout handling
- **Invalid Commands** - Helpful suggestions for correct usage
- **Permission Errors** - Guidance on required permissions
- **Rate Limiting** - Automatic backoff and retry strategies

## Logging

### Log Levels

- `DEBUG` - Detailed debugging information
- `INFO` - General information about operations
- `WARNING` - Warning messages about potential issues
- `ERROR` - Error messages for failed operations
- `CRITICAL` - Critical errors that may stop execution

### Log Configuration

```bash
# Set log level
export TALOS_LOG_LEVEL=DEBUG

# Set log file
export TALOS_LOG_FILE=talos.log

# Enable verbose output
uv run talos --verbose
```

## Getting Help

### Command Help

Get help for any command:

```bash
uv run talos --help
uv run talos twitter --help
uv run talos github --help
```

### Interactive Help

In interactive mode, you can ask for help:

```
>> help
>> what commands are available?
>> how do I analyze Twitter sentiment?
```

### Documentation

- **CLI Reference** - Detailed command documentation
- **Examples** - Common usage patterns and workflows
- **Troubleshooting** - Solutions for common issues
- **API Reference** - Technical details about the underlying APIs

## Best Practices

### Security

- **Environment Variables** - Use environment variables for API keys
- **File Permissions** - Secure configuration files with appropriate permissions
- **Key Rotation** - Regularly rotate API keys and tokens
- **Audit Logs** - Monitor CLI usage through log files

### Performance

- **Batch Operations** - Use batch commands when possible
- **Caching** - Enable caching for frequently accessed data
- **Rate Limiting** - Respect API rate limits to avoid throttling
- **Resource Management** - Monitor memory and CPU usage

### Workflow Integration

- **Scripting** - Use non-interactive mode for automation
- **CI/CD Integration** - Integrate with continuous integration pipelines
- **Monitoring** - Set up alerts for daemon mode operations
- **Backup** - Regular backup of configuration and data files

This CLI provides a powerful interface for managing decentralized protocols through the Talos AI agent system.
