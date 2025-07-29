# Memory CLI

The memory CLI module provides commands for managing and searching the agent's persistent memory system.

## Commands

### `list` - List Memories

List all memories with optional user filtering.

```bash
uv run talos memory list [options]
```

**Options:**
- `--user-id, -u`: User ID to filter memories by
- `--filter-user`: Filter memories by a different user
- `--use-database`: Use database backend instead of files (default: true)
- `--verbose, -v`: Enable verbose output

### `search` - Search Memories

Search memories using semantic similarity with optional user filtering.

```bash
uv run talos memory search <query> [options]
```

**Arguments:**
- `query`: Search query for memories (required)

**Options:**
- `--user-id, -u`: User ID to search memories for
- `--filter-user`: Filter memories by a different user
- `--limit, -l`: Maximum number of results to return (default: 5)
- `--use-database`: Use database backend instead of files (default: true)
- `--verbose, -v`: Enable verbose output

### `flush` - Flush Memories

Flush unsaved memories to disk or delete user memories from database.

```bash
uv run talos memory flush [options]
```

**Options:**
- `--user-id, -u`: User ID for database backend (if not provided with database backend, flushes ALL memories after confirmation)
- `--use-database`: Use database backend instead of files (default: true)
- `--verbose, -v`: Enable verbose output

## Usage Examples

### Listing Memories

```bash
# List all memories
uv run talos memory list

# List memories for a specific user
uv run talos memory list --user-id user123

# List memories with verbose output
uv run talos memory list --verbose

# Use file-based backend
uv run talos memory list --no-use-database
```

### Searching Memories

```bash
# Basic semantic search
uv run talos memory search "governance proposal"

# Search with custom limit
uv run talos memory search "twitter sentiment" --limit 10

# Search for specific user's memories
uv run talos memory search "market analysis" --user-id user123

# Search with verbose output
uv run talos memory search "protocol upgrade" --verbose
```

### Managing Memory Storage

```bash
# Flush unsaved memories for a specific user
uv run talos memory flush --user-id user123

# Flush all memories (requires confirmation)
uv run talos memory flush

# Flush with file-based backend
uv run talos memory flush --no-use-database
```

## Memory Backends

### Database Backend (Default)

The database backend provides:
- Multi-user support with user isolation
- Persistent storage across sessions
- Efficient semantic search using vector embeddings
- User management and cleanup capabilities

### File Backend

The file backend provides:
- Simple file-based storage
- Single-user operation
- Local memory and history files
- No user isolation

## Memory Structure

Each memory contains:
- **Description**: Text content of the memory
- **Timestamp**: When the memory was created
- **Metadata**: Additional context and tags
- **Embeddings**: Vector representations for semantic search

## Environment Variables

- `OPENAI_API_KEY`: Required for generating embeddings for semantic search

## Database Operations

### User Management

When using the database backend:
- Temporary user IDs are generated if not provided
- User memories are isolated from each other
- Cleanup operations can remove old temporary users

### Memory Persistence

- Memories are automatically saved to the database
- Unsaved memories can be flushed manually
- Search operations use vector similarity matching

## Error Handling

The memory CLI includes comprehensive error handling for:
- Database connection issues
- Missing user IDs
- Invalid search queries
- File system permissions (file backend)
- API connectivity for embeddings

## Integration

The memory system integrates with:
- Main Talos agent for conversation history
- All CLI modules for persistent context
- Database cleanup operations
- User management system
