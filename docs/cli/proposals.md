# Proposals CLI

The proposals CLI module provides commands for evaluating governance proposals using AI analysis.

## Commands

### `eval` - Evaluate Proposal

Evaluates a governance proposal from a file using AI analysis.

```bash
uv run talos proposals eval --file <filepath>
```

**Arguments:**
- `--file, -f`: Path to the proposal file (required)

**Options:**
- `--model-name`: LLM model to use (default: "gpt-4o")
- `--temperature`: Temperature for LLM generation (default: 0.0)

## Usage Examples

### Basic Proposal Evaluation

```bash
# Evaluate a proposal from a text file
uv run talos proposals eval --file governance_proposal.txt

# Use a different model
uv run talos proposals eval --file proposal.md --model-name gpt-4o --temperature 0.1
```

### Proposal File Format

The proposal file should contain the full text of the governance proposal. Supported formats include:

- Plain text (.txt)
- Markdown (.md)
- Any text-based format

Example proposal file content:
```
# Governance Proposal: Treasury Allocation

## Summary
This proposal requests allocation of 100,000 tokens from the treasury for development funding.

## Details
The funds will be used for:
1. Core development team salaries
2. Security audits
3. Infrastructure costs

## Timeline
- Phase 1: 30 days
- Phase 2: 60 days
- Phase 3: 90 days

## Budget Breakdown
- Development: 60,000 tokens
- Security: 25,000 tokens
- Infrastructure: 15,000 tokens
```

## Output

The command provides a comprehensive analysis including:

- **Summary**: Brief overview of the proposal
- **Risk Assessment**: Potential risks and concerns
- **Benefits Analysis**: Expected benefits and outcomes
- **Recommendation**: AI-generated recommendation (approve/reject/modify)
- **Reasoning**: Detailed explanation of the recommendation

## Environment Variables

- `OPENAI_API_KEY`: Required for AI analysis functionality

## Error Handling

The command includes error handling for:
- Missing or invalid file paths
- File reading permissions
- API connectivity issues
- Invalid proposal formats

## Integration

The proposals CLI integrates with the main Talos agent system and can be used as part of automated governance workflows or manual proposal review processes.
