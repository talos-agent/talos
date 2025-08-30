# GitHub Commands

The Talos CLI includes comprehensive GitHub integration for repository management, pull request reviews, and development workflow automation.

## Setup

### Authentication

Set your GitHub API token as an environment variable:

```bash
export GITHUB_API_TOKEN=your_github_token_here
```

### Repository Configuration

Specify the target repository in two ways:

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

List pull requests for a repository with filtering options.

**Basic Usage:**
```bash
# List open PRs (default)
uv run talos github get-prs --repo microsoft/vscode

# Using environment variable
export GITHUB_REPO=microsoft/vscode
uv run talos github get-prs
```

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'
- `--state`: PR state - 'open' (default), 'closed', or 'all'

**Examples:**
```bash
# List all PRs (open, closed, merged)
uv run talos github get-prs --repo microsoft/vscode --state all

# List closed PRs only
uv run talos github get-prs --repo microsoft/vscode --state closed
```

**Output Format:**
```
PR #123: Fix memory leak in parser
  Author: developer@example.com
  State: open
  Created: 2024-01-15
  Updated: 2024-01-16
  
PR #122: Add new API endpoint
  Author: contributor@example.com
  State: merged
  Created: 2024-01-14
  Merged: 2024-01-15
```

### `review-pr` - AI-Powered PR Review

Perform comprehensive AI analysis of pull requests with security and quality scoring.

**Basic Usage:**
```bash
# Review a PR (display results only)
uv run talos github review-pr 123 --repo microsoft/vscode

# Review and post the review as a comment on GitHub
uv run talos github review-pr 123 --repo microsoft/vscode --post
```

**Arguments:**
- `pr_number`: Pull request number to review (required)

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'
- `--post`: Post the review as a comment on the PR
- `--auto-approve`: Automatically approve if criteria are met

**Advanced Usage:**
```bash
# Review with auto-approval if criteria are met
uv run talos github review-pr 123 --repo microsoft/vscode --auto-approve

# Review multiple PRs
for pr in 123 124 125; do
  uv run talos github review-pr $pr --repo microsoft/vscode --post
done
```

**Review Output:**

The review includes comprehensive analysis:

```
=== PR Review Analysis ===

Security Score: 85/100
Quality Score: 92/100
Recommendation: APPROVE

=== Security Analysis ===
✅ No hardcoded secrets detected
✅ Input validation present
⚠️  Consider adding rate limiting to new API endpoint
✅ Authentication checks in place

=== Quality Analysis ===
✅ Code follows project style guidelines
✅ Adequate test coverage (87%)
✅ Documentation updated
⚠️  Consider adding error handling for edge case

=== Detailed Findings ===
1. New API endpoint properly validates input parameters
2. Tests cover main functionality but missing edge case tests
3. Documentation clearly explains new features
4. No breaking changes detected

=== Recommendations ===
- Add rate limiting to prevent abuse
- Include tests for malformed input handling
- Consider adding metrics collection

Overall: This PR introduces valuable functionality with good security practices. 
Minor improvements suggested but safe to merge.
```

### `approve-pr` - Force Approve PR

Approve a pull request without AI analysis (use with caution).

**Usage:**
```bash
uv run talos github approve-pr 123 --repo microsoft/vscode
```

**Arguments:**
- `pr_number`: Pull request number to approve (required)

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'

**When to Use:**
- Emergency fixes that need immediate approval
- PRs that have been manually reviewed
- Trusted contributors with pre-approved changes

### `merge-pr` - Merge Pull Request

Merge an approved pull request.

**Usage:**
```bash
uv run talos github merge-pr 123 --repo microsoft/vscode
```

**Arguments:**
- `pr_number`: Pull request number to merge (required)

**Options:**
- `--repo, -r`: Repository in format 'owner/repo'

**Prerequisites:**
- PR must be approved
- All required checks must pass
- No merge conflicts
- Sufficient permissions

## Workflow Examples

### Daily PR Review Workflow

```bash
#!/bin/bash
# daily-review.sh

export GITHUB_REPO=myorg/myproject

echo "=== Daily PR Review ==="

# List all open PRs
echo "Open PRs:"
uv run talos github get-prs

# Review each open PR
for pr in $(uv run talos github get-prs --format=numbers); do
  echo "Reviewing PR #$pr..."
  uv run talos github review-pr $pr --post
done

echo "Review complete!"
```

### Automated Security Review

```bash
#!/bin/bash
# security-review.sh

export GITHUB_REPO=myorg/sensitive-project

# Get PRs from external contributors
external_prs=$(uv run talos github get-prs --external-only)

for pr in $external_prs; do
  echo "Security review for external PR #$pr"
  
  # Perform detailed review without auto-approval
  uv run talos github review-pr $pr --security-focus --post
  
  # Only approve if security score > 90
  score=$(uv run talos github review-pr $pr --get-security-score)
  if [ $score -gt 90 ]; then
    uv run talos github approve-pr $pr
    echo "PR #$pr approved (security score: $score)"
  else
    echo "PR #$pr requires manual review (security score: $score)"
  fi
done
```

### Release Preparation

```bash
#!/bin/bash
# release-prep.sh

export GITHUB_REPO=myorg/myproject

echo "=== Release Preparation ==="

# Review all PRs targeted for release
release_prs=$(uv run talos github get-prs --label="release-candidate")

for pr in $release_prs; do
  echo "Final review for release PR #$pr"
  
  # Comprehensive review with strict criteria
  uv run talos github review-pr $pr --strict-mode --post
  
  # Auto-approve only high-quality PRs
  uv run talos github review-pr $pr --auto-approve --min-quality=95
done

echo "Release review complete!"
```

## Configuration

### Review Criteria

Configure review criteria in your Talos configuration:

```yaml
github:
  review:
    security:
      min_score: 80
      required_checks:
        - "no_hardcoded_secrets"
        - "input_validation"
        - "authentication"
    
    quality:
      min_score: 85
      required_checks:
        - "test_coverage"
        - "documentation"
        - "style_compliance"
    
    auto_approve:
      enabled: true
      min_security_score: 90
      min_quality_score: 90
      trusted_authors:
        - "senior-dev@company.com"
        - "security-team@company.com"
```

### Notification Settings

```yaml
github:
  notifications:
    slack_webhook: "https://hooks.slack.com/..."
    email_alerts: true
    
    triggers:
      - "security_score_low"
      - "quality_score_low"
      - "external_contributor"
      - "large_pr"
```

## Error Handling

The GitHub commands include comprehensive error handling:

### Common Errors

**Missing Repository:**
```
Error: Repository not specified
Solution: Set GITHUB_REPO environment variable or use --repo flag
```

**Invalid Token:**
```
Error: GitHub API authentication failed
Solution: Check GITHUB_API_TOKEN environment variable
```

**PR Not Found:**
```
Error: Pull request #123 not found
Solution: Verify PR number and repository access
```

**Insufficient Permissions:**
```
Error: Insufficient permissions to approve PR
Solution: Check repository permissions for your GitHub token
```

### Rate Limiting

GitHub API has rate limits. Talos handles this automatically:

- **Automatic Backoff** - Waits when rate limit is reached
- **Batch Operations** - Optimizes API calls for efficiency
- **Progress Updates** - Shows progress for long-running operations

### Network Issues

**Retry Logic:**
- Automatic retry for transient network errors
- Exponential backoff for repeated failures
- Clear error messages for permanent failures

## Best Practices

### Security

- **Token Security** - Store GitHub tokens securely
- **Permission Scope** - Use minimal required permissions
- **Review External PRs** - Always review PRs from external contributors
- **Audit Logs** - Monitor all GitHub operations

### Efficiency

- **Batch Reviews** - Review multiple PRs in scripts
- **Environment Variables** - Use GITHUB_REPO for repeated operations
- **Filtering** - Use state and label filters to focus on relevant PRs
- **Automation** - Integrate with CI/CD pipelines

### Quality Assurance

- **Consistent Reviews** - Use standardized review criteria
- **Documentation** - Ensure all reviews are documented
- **Follow-up** - Track and follow up on review recommendations
- **Continuous Improvement** - Regularly update review criteria

The GitHub integration provides powerful tools for maintaining code quality and security while automating routine development workflows.
