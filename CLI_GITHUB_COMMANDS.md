# GitHub CLI Commands

The Talos CLI includes a GitHub sub-app with commands for managing pull requests.

## Setup

Set your GitHub API token as an environment variable:
```bash
export GITHUB_API_TOKEN=your_github_token_here
```

## Repository Parameter

All GitHub commands require a target repository. You can specify it in two ways:

1. **Environment variable** (recommended for repeated use):
   ```bash
   export GITHUB_REPO=owner/repo
   uv run talos github get-prs
   ```

2. **Command line argument**:
   ```bash
   uv run talos github get-prs --repo owner/repo
   ```

## Commands

### `get-prs` - List Pull Requests

List all pull requests for a repository.

```bash
# List open PRs (default)
uv run talos github get-prs --repo microsoft/vscode

# List all PRs (open, closed, merged)
uv run talos github get-prs --repo microsoft/vscode --state all

# List closed PRs
uv run talos github get-prs --repo microsoft/vscode --state closed
```

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'
- `--state`: PR state - 'open' (default), 'closed', or 'all'

### `review-pr` - AI-Powered PR Review

Review a pull request using AI analysis with security and quality scoring.

```bash
# Review a PR (display results only)
uv run talos github review-pr 123 --repo microsoft/vscode

# Review and post the review as a comment on GitHub
uv run talos github review-pr 123 --repo microsoft/vscode --post

# Review with auto-approval if criteria are met
uv run talos github review-pr 123 --repo microsoft/vscode --auto-approve
```

**Arguments:**
- `pr_number`: Pull request number to review

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'
- `--post`: Post the review as a comment on the PR
- `--auto-approve`: Automatically approve if criteria are met

**Output includes:**
- Detailed review analysis
- Security score (0-100)
- Quality score (0-100)
- Recommendation (approve/request changes/etc.)
- Reasoning for the recommendation

### `approve-pr` - Force Approve PR

Force approve a pull request without AI analysis.

```bash
uv run talos github approve-pr 123 --repo microsoft/vscode
```

**Arguments:**
- `pr_number`: Pull request number to approve

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'

### `merge-pr` - Merge Pull Request

Merge a pull request.

```bash
uv run talos github merge-pr 123 --repo microsoft/vscode
```

**Arguments:**
- `pr_number`: Pull request number to merge

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'

## Examples

```bash
# Set up environment
export GITHUB_API_TOKEN=ghp_your_token_here
export GITHUB_REPO=microsoft/vscode

# List open PRs
uv run talos github get-prs

# Review PR #123 and post the review
uv run talos github review-pr 123 --post

# Approve PR #123
uv run talos github approve-pr 123

# Merge PR #123
uv run talos github merge-pr 123
```

## Error Handling

The commands include comprehensive error handling for:
- Missing or invalid repository format
- Missing GitHub API token
- Network connectivity issues
- GitHub API rate limiting
- Invalid PR numbers
- Insufficient permissions

All errors are displayed with helpful messages to guide troubleshooting.
