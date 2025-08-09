# Talos CLI

The Talos CLI is the main entry point for interacting with the Talos agent.

## Installation

The CLI is installed as part of the `talos` package.

## Usage

The CLI can be run in multiple modes: interactive, non-interactive, and daemon mode.

### Interactive Mode

To enter interactive mode, run `talos` without any arguments:

```bash
uv run talos
>> your query
```

### Non-Interactive Mode

In non-interactive mode, you can run a single query and the agent will exit:

```bash
uv run talos "your query"
```

### Daemon Mode

Run the agent continuously for scheduled operations:

```bash
uv run talos daemon
```

## Commands

The Talos CLI has the following commands and subcommands:

### `twitter`

Twitter-related operations and analysis.

#### `get-user-prompt <username>`

Gets the general voice of a user as a structured persona analysis.

```bash
uv run talos twitter get-user-prompt <username>
```

#### `get-query-sentiment <query> [--start-time]`

Gets the general sentiment/report on a specific query.

```bash
uv run talos twitter get-query-sentiment <query>
uv run talos twitter get-query-sentiment <query> --start-time "2023-01-01T00:00:00Z"
```

#### `integrate-voice [--username]`

Integrate Twitter voice analysis into agent communication.

```bash
uv run talos twitter integrate-voice
uv run talos twitter integrate-voice --username talos_is
```

### `github`

GitHub repository management and PR reviews. See [GitHub CLI Commands](../CLI_GITHUB_COMMANDS.md) for detailed documentation.

### `proposals`

Governance proposal evaluation.

#### `eval --file <filepath>`

Evaluates a proposal from a file.

```bash
uv run talos proposals eval --file proposal.txt
```

### `memory`

Memory management and search operations.

#### `list [--user-id] [--filter-user] [--use-database] [--verbose]`

List all memories with optional user filtering.

```bash
uv run talos memory list
uv run talos memory list --user-id user123 --verbose
```

#### `search <query> [--user-id] [--limit] [--use-database]`

Search memories using semantic similarity.

```bash
uv run talos memory search "governance proposal"
uv run talos memory search "twitter sentiment" --limit 10
```

#### `flush [--user-id] [--use-database]`

Flush unsaved memories to disk or delete user memories.

```bash
uv run talos memory flush --user-id user123
```

### `arbiscan`

Arbitrum blockchain contract source code retrieval.

#### `get-source-code <contract_address> [--api-key] [--chain-id] [--format]`

Gets the source code of a verified smart contract from Arbiscan.

```bash
uv run talos arbiscan get-source-code 0x1234...
uv run talos arbiscan get-source-code 0x1234... --format json
uv run talos arbiscan get-source-code 0x1234... --chain-id 42170
```

### Core Commands

#### `generate-keys [--key-dir]`

Generates a new RSA key pair.

```bash
uv run talos generate-keys
uv run talos generate-keys --key-dir /path/to/keys
```

#### `get-public-key [--key-dir]`

Gets the public key.

```bash
uv run talos get-public-key
```

#### `encrypt <data> <public_key_file>`

Encrypts a message.

```bash
uv run talos encrypt "secret message" public_key.pem
```

#### `decrypt <encrypted_data> [--key-dir]`

Decrypts a message.

```bash
uv run talos decrypt <base64_encrypted_data>
```

#### `daemon [--prompts-dir] [--model-name] [--temperature]`

Run the Talos agent in daemon mode for continuous operation.

```bash
uv run talos daemon
uv run talos daemon --model-name gpt-5 --temperature 0.1
```

#### `cleanup-users [--older-than] [--dry-run]`

Clean up temporary users and their conversation data.

```bash
uv run talos cleanup-users --older-than 24 --dry-run
uv run talos cleanup-users --older-than 48
```

#### `db-stats`

Show database statistics.

```bash
uv run talos db-stats
```

## Global Options

- `--verbose, -v`: Enable verbose output
- `--user-id, -u`: User identifier for conversation tracking
- `--use-database`: Use database for conversation storage instead of files
- `--help`: Show help information

## Environment Variables

### Required
- `OPENAI_API_KEY`: OpenAI API key for AI functionality
- `PINATA_API_KEY`: Pinata API key for IPFS operations
- `PINATA_SECRET_API_KEY`: Pinata secret API key for IPFS operations

### Optional
- `GITHUB_API_TOKEN`: GitHub API token for repository operations
- `TWITTER_BEARER_TOKEN`: Twitter Bearer token for social media analysis
- `ARBISCAN_API_KEY`: Arbiscan API key for higher rate limits
