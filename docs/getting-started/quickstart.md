# Quick Start

Get up and running with Talos in just a few minutes.

## Basic Setup

1. **Install Talos** (see [Installation](installation.md) for details):
   ```bash
   git clone https://github.com/talos-agent/talos.git
   cd talos
   uv venv && source .venv/bin/activate
   ./scripts/install_deps.sh
   ```

2. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export PINATA_API_KEY="your-pinata-api-key"
   export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
   ```

## Usage Modes

### Interactive CLI

Start an interactive conversation with Talos:

```bash
uv run talos
```

You'll see a prompt where you can ask questions or give commands:

```
>> What are your main capabilities?
>> Analyze the sentiment around "DeFi protocols" on Twitter
>> Help me evaluate a governance proposal
```

Type `exit` to quit the interactive session.

### Single Query Mode

Run a single query and exit:

```bash
uv run talos "What is the current market sentiment?"
```

### Daemon Mode

Run Talos continuously for scheduled operations:

```bash
export GITHUB_API_TOKEN="your-github-token"
export TWITTER_BEARER_TOKEN="your-twitter-bearer-token"
uv run talos daemon
```

The daemon will:
- Execute scheduled jobs
- Monitor for new proposals
- Perform continuous market analysis
- Handle automated responses

## Common Commands

### Twitter Analysis
```bash
# Get user sentiment analysis
uv run talos twitter get-user-prompt username

# Analyze query sentiment
uv run talos twitter get-query-sentiment "DeFi yield farming"
```

### GitHub Operations
```bash
# Set up GitHub repository
export GITHUB_REPO=owner/repo

# List pull requests
uv run talos github get-prs

# Review a pull request
uv run talos github review-pr 123 --post

# Approve a pull request
uv run talos github approve-pr 123
```

### Cryptography
```bash
# Generate RSA key pair
uv run talos generate-keys

# Get public key
uv run talos get-public-key

# Encrypt data
uv run talos encrypt "secret message" public_key.pem

# Decrypt data
uv run talos decrypt "encrypted_data"
```

## Example Workflows

### Proposal Evaluation

1. **Run the proposal example**:
   ```bash
   python proposal_example.py
   ```

2. **Interactive proposal analysis**:
   ```bash
   uv run talos
   >> I need help evaluating a governance proposal about increasing staking rewards
   ```

### Market Analysis

```bash
uv run talos
>> Analyze the current market conditions for ETH
>> What's the sentiment around yield farming protocols?
>> Should we adjust our staking APR based on current conditions?
```

### GitHub Management

```bash
# Set up environment
export GITHUB_API_TOKEN=your_token
export GITHUB_REPO=your-org/your-repo

# Review recent PRs
uv run talos github get-prs --state all

# Get AI review of a specific PR
uv run talos github review-pr 42 --post
```

## Next Steps

- **Learn the Architecture**: Understand how Talos works by reading the [Architecture](../architecture/components.md) documentation
- **Explore CLI Commands**: Check out the complete [CLI Reference](../cli/overview.md)
- **Contribute**: See the [Development](../development/contributing.md) guide to contribute to the project
- **Advanced Usage**: Learn about the [Philosophy](../philosophy/vision.md) and roadmap behind Talos

## Getting Help

- Check the [CLI Reference](../cli/overview.md) for detailed command documentation
- Review [Development](../development/contributing.md) for troubleshooting
- Open an issue on [GitHub](https://github.com/talos-agent/talos) for bugs or feature requests
