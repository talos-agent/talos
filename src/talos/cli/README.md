# Talos CLI

The Talos CLI is the main entry point for interacting with the Talos agent.

## Installation

The CLI is installed as part of the `talos` package.

## Usage

The CLI can be run in two modes: interactive and non-interactive.

### Non-Interactive Mode

In non-interactive mode, you can run a single query and the agent will exit.

```bash
talos "your query"
```

### Interactive Mode

To enter interactive mode, run `talos` without any arguments.

```bash
talos
>> your query
```

## Commands

The Talos CLI has the following commands:

### `twitter`

This command has subcommands for interacting with Twitter.

#### `get-user-prompt <username>`

Gets the general voice of a user as a prompt.

```bash
talos twitter get-user-prompt <username>
```

#### `get-query-sentiment <query>`

Gets the general sentiment/report on a specific query.

```bash
talos twitter get-query-sentiment <query>
```

### `generate-keys`

Generates a new RSA key pair.

```bash
talos generate-keys
```

### `get-public-key`

Gets the public key.

```bash
talos get-public-key
```

### `encrypt <data> <public_key_file>`

Encrypts a message.

```bash
talos encrypt <data> <public_key_file>
```

### `decrypt <encrypted_data>`

Decrypts a message.

```bash
talos decrypt <encrypted_data>
```
