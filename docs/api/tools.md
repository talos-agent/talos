# Tools API Reference

This document provides detailed API reference for the tools layer of the Talos system, which handles external integrations and utilities.

## Base Tool Interface

### BaseTool

Abstract base class for all tools in the Talos system.

```python
from abc import ABC, abstractmethod

class BaseTool(ABC):
    name: str
    description: str
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool with provided arguments."""
        pass
```

### SupervisedTool

Wrapper that adds hypervisor approval to any tool.

```python
class SupervisedTool:
    def __init__(self, base_tool: BaseTool, supervisor: Supervisor):
        """Wrap a tool with supervision.
        
        Args:
            base_tool: The tool to wrap
            supervisor: Supervisor for approval decisions
        """
        self.base_tool = base_tool
        self.supervisor = supervisor
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute tool with supervisor approval."""
```

## GitHub Tools

### GithubTools

Comprehensive GitHub API integration for repository management.

```python
class GithubTools:
    def __init__(self, token: str):
        """Initialize GitHub tools.
        
        Args:
            token: GitHub API token with appropriate permissions
        """
```

#### Repository Operations

##### `get_all_pull_requests(user: str, project: str, state: str = "open") -> List[dict]`

Retrieve pull requests from a repository.

**Parameters:**
- `user` (str): Repository owner
- `project` (str): Repository name
- `state` (str): PR state - "open", "closed", or "all"

**Returns:**
- `List[dict]`: List of pull request data

**Example:**
```python
from talos.tools.github import GithubTools

github = GithubTools(token="your-token")
prs = github.get_all_pull_requests("microsoft", "vscode", state="open")

for pr in prs:
    print(f"PR #{pr['number']}: {pr['title']}")
    print(f"Author: {pr['user']['login']}")
    print(f"State: {pr['state']}")
```

##### `get_open_issues(user: str, project: str) -> List[dict]`

Retrieve open issues from a repository.

**Parameters:**
- `user` (str): Repository owner
- `project` (str): Repository name

**Returns:**
- `List[dict]`: List of issue data

##### `review_pull_request(user: str, project: str, pr_number: int) -> dict`

Perform AI-powered review of a pull request.

**Parameters:**
- `user` (str): Repository owner
- `project` (str): Repository name
- `pr_number` (int): Pull request number

**Returns:**
- `dict`: Review analysis with security and quality scores

**Example:**
```python
review = github.review_pull_request("owner", "repo", 123)
print(f"Security Score: {review['security_score']}/100")
print(f"Quality Score: {review['quality_score']}/100")
print(f"Recommendation: {review['recommendation']}")
print(f"Analysis: {review['detailed_analysis']}")
```

##### `approve_pull_request(user: str, project: str, pr_number: int) -> bool`

Approve a pull request.

**Parameters:**
- `user` (str): Repository owner
- `project` (str): Repository name
- `pr_number` (int): Pull request number

**Returns:**
- `bool`: True if approval was successful

##### `merge_pull_request(user: str, project: str, pr_number: int) -> bool`

Merge an approved pull request.

**Parameters:**
- `user` (str): Repository owner
- `project` (str): Repository name
- `pr_number` (int): Pull request number

**Returns:**
- `bool`: True if merge was successful

## Twitter Tools

### TwitterTools

Twitter API integration for social media monitoring and analysis.

```python
class TwitterTools:
    def __init__(self, bearer_token: str):
        """Initialize Twitter tools.
        
        Args:
            bearer_token: Twitter API Bearer Token
        """
```

#### Search and Analysis

##### `search_tweets(query: str, limit: int = 100) -> List[dict]`

Search for tweets matching a query.

**Parameters:**
- `query` (str): Search query
- `limit` (int): Maximum number of tweets to return

**Returns:**
- `List[dict]`: List of tweet data

**Example:**
```python
from talos.tools.twitter import TwitterTools

twitter = TwitterTools(bearer_token="your-token")
tweets = twitter.search_tweets("DeFi yield farming", limit=50)

for tweet in tweets:
    print(f"@{tweet['author']['username']}: {tweet['text']}")
    print(f"Likes: {tweet['public_metrics']['like_count']}")
```

##### `get_user_tweets(username: str, limit: int = 100) -> List[dict]`

Get recent tweets from a specific user.

**Parameters:**
- `username` (str): Twitter username (without @)
- `limit` (int): Maximum number of tweets to return

**Returns:**
- `List[dict]`: List of tweet data

##### `analyze_sentiment(tweets: List[dict]) -> dict`

Analyze sentiment of a collection of tweets.

**Parameters:**
- `tweets` (List[dict]): List of tweet data

**Returns:**
- `dict`: Sentiment analysis results

**Example:**
```python
tweets = twitter.search_tweets("protocol governance", limit=200)
sentiment = twitter.analyze_sentiment(tweets)

print(f"Overall sentiment: {sentiment['overall_sentiment']}")
print(f"Positive: {sentiment['positive_ratio']:.1%}")
print(f"Negative: {sentiment['negative_ratio']:.1%}")
print(f"Neutral: {sentiment['neutral_ratio']:.1%}")
```

##### `get_trending_topics(location: str = "worldwide") -> List[str]`

Get trending topics for a location.

**Parameters:**
- `location` (str): Location for trends (default: "worldwide")

**Returns:**
- `List[str]`: List of trending topics

#### User Analysis

##### `analyze_user_influence(username: str) -> dict`

Analyze a user's influence and credibility.

**Parameters:**
- `username` (str): Twitter username (without @)

**Returns:**
- `dict`: User influence analysis

**Example:**
```python
influence = twitter.analyze_user_influence("vitalikbuterin")
print(f"Influence Score: {influence['influence_score']}/100")
print(f"Follower Quality: {influence['follower_quality']}")
print(f"Engagement Rate: {influence['engagement_rate']:.2%}")
print(f"Expertise Areas: {', '.join(influence['expertise_areas'])}")
```

## IPFS Tools

### IPFSTools

IPFS integration for decentralized storage operations.

```python
class IPFSTools:
    def __init__(self, api_key: str, secret_key: str):
        """Initialize IPFS tools.
        
        Args:
            api_key: Pinata API key
            secret_key: Pinata secret key
        """
```

#### Storage Operations

##### `upload_json(data: dict, name: str) -> str`

Upload JSON data to IPFS.

**Parameters:**
- `data` (dict): JSON data to upload
- `name` (str): Name for the uploaded content

**Returns:**
- `str`: IPFS hash of uploaded content

**Example:**
```python
from talos.tools.ipfs import IPFSTools

ipfs = IPFSTools(api_key="your-key", secret_key="your-secret")

proposal_data = {
    "title": "Increase Staking Rewards",
    "description": "Proposal to increase staking rewards from 5% to 8%",
    "voting_period": "7 days",
    "created_at": "2024-01-15T10:00:00Z"
}

ipfs_hash = ipfs.upload_json(proposal_data, "governance-proposal-001")
print(f"Proposal uploaded to IPFS: {ipfs_hash}")
print(f"Access URL: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
```

##### `upload_text(content: str, name: str) -> str`

Upload text content to IPFS.

**Parameters:**
- `content` (str): Text content to upload
- `name` (str): Name for the uploaded content

**Returns:**
- `str`: IPFS hash of uploaded content

##### `retrieve_content(ipfs_hash: str) -> str`

Retrieve content from IPFS by hash.

**Parameters:**
- `ipfs_hash` (str): IPFS hash of content to retrieve

**Returns:**
- `str`: Retrieved content

##### `pin_content(ipfs_hash: str) -> bool`

Pin content to ensure it remains available.

**Parameters:**
- `ipfs_hash` (str): IPFS hash to pin

**Returns:**
- `bool`: True if pinning was successful

## Cryptography Tools

### CryptographyTools

RSA encryption and decryption operations.

```python
class CryptographyTools:
    def __init__(self, key_dir: str = ".keys"):
        """Initialize cryptography tools.
        
        Args:
            key_dir: Directory containing RSA keys
        """
```

#### Key Management

##### `generate_key_pair(key_size: int = 2048) -> Tuple[str, str]`

Generate RSA key pair.

**Parameters:**
- `key_size` (int): Key size in bits (1024, 2048, or 4096)

**Returns:**
- `Tuple[str, str]`: (private_key_path, public_key_path)

**Example:**
```python
from talos.tools.crypto import CryptographyTools

crypto = CryptographyTools()
private_key, public_key = crypto.generate_key_pair(key_size=2048)
print(f"Keys generated: {private_key}, {public_key}")
```

##### `get_public_key() -> str`

Get the current public key.

**Returns:**
- `str`: Public key in PEM format

##### `get_key_fingerprint() -> str`

Get fingerprint of the current key pair.

**Returns:**
- `str`: SHA256 fingerprint of the public key

#### Encryption Operations

##### `encrypt_data(data: str, public_key_path: str) -> str`

Encrypt data using RSA public key.

**Parameters:**
- `data` (str): Data to encrypt
- `public_key_path` (str): Path to public key file

**Returns:**
- `str`: Base64-encoded encrypted data

**Example:**
```python
# Encrypt sensitive data
encrypted = crypto.encrypt_data(
    "Secret protocol configuration",
    "recipient_public_key.pem"
)
print(f"Encrypted data: {encrypted}")
```

##### `decrypt_data(encrypted_data: str) -> str`

Decrypt data using RSA private key.

**Parameters:**
- `encrypted_data` (str): Base64-encoded encrypted data

**Returns:**
- `str`: Decrypted plaintext data

**Example:**
```python
# Decrypt received data
decrypted = crypto.decrypt_data(encrypted_data)
print(f"Decrypted: {decrypted}")
```

##### `sign_data(data: str) -> str`

Create digital signature for data.

**Parameters:**
- `data` (str): Data to sign

**Returns:**
- `str`: Base64-encoded signature

##### `verify_signature(data: str, signature: str, public_key_path: str) -> bool`

Verify digital signature.

**Parameters:**
- `data` (str): Original data
- `signature` (str): Base64-encoded signature
- `public_key_path` (str): Path to public key file

**Returns:**
- `bool`: True if signature is valid

## Tool Manager

### ToolManager

Central registry and manager for all tools.

```python
class ToolManager:
    def __init__(self):
        """Initialize tool manager."""
        self.tools: Dict[str, BaseTool] = {}
        self.supervised_tools: Dict[str, SupervisedTool] = {}
```

#### Tool Registration

##### `register_tool(tool: BaseTool) -> None`

Register a tool with the manager.

**Parameters:**
- `tool` (BaseTool): Tool to register

##### `register_supervised_tool(tool: BaseTool, supervisor: Supervisor) -> None`

Register a tool with supervision.

**Parameters:**
- `tool` (BaseTool): Tool to register
- `supervisor` (Supervisor): Supervisor for approval

##### `get_tool(name: str) -> Optional[BaseTool]`

Get a registered tool by name.

**Parameters:**
- `name` (str): Tool name

**Returns:**
- `Optional[BaseTool]`: Tool instance or None

**Example:**
```python
from talos.core.tool_manager import ToolManager
from talos.tools.github import GithubTools
from talos.hypervisor.supervisor import RuleBasedSupervisor

# Create tool manager
tool_manager = ToolManager()

# Register tools
github_tool = GithubTools(token="your-token")
supervisor = RuleBasedSupervisor()

tool_manager.register_supervised_tool(github_tool, supervisor)

# Use tools
github = tool_manager.get_tool("github")
if github:
    prs = github.get_all_pull_requests("owner", "repo")
```

## Usage Examples

### Comprehensive GitHub Workflow

```python
from talos.tools.github import GithubTools
from talos.hypervisor.supervisor import RuleBasedSupervisor
from talos.core.tool_manager import SupervisedTool

# Set up supervised GitHub operations
github = GithubTools(token="your-token")
supervisor = RuleBasedSupervisor()
supervised_github = SupervisedTool(github, supervisor)

# Automated PR review workflow
def review_repository_prs(owner: str, repo: str):
    # Get all open PRs
    prs = supervised_github.execute("get_all_pull_requests", owner, repo, "open")
    
    for pr in prs:
        print(f"Reviewing PR #{pr['number']}: {pr['title']}")
        
        # Perform AI review
        review = supervised_github.execute("review_pull_request", owner, repo, pr['number'])
        
        print(f"Security Score: {review['security_score']}/100")
        print(f"Quality Score: {review['quality_score']}/100")
        
        # Auto-approve if criteria are met
        if review['security_score'] >= 85 and review['quality_score'] >= 90:
            supervised_github.execute("approve_pull_request", owner, repo, pr['number'])
            print(f"PR #{pr['number']} approved automatically")
        else:
            print(f"PR #{pr['number']} requires manual review")

review_repository_prs("your-org", "your-repo")
```

### Social Media Sentiment Pipeline

```python
from talos.tools.twitter import TwitterTools
from talos.tools.ipfs import IPFSTools

# Set up tools
twitter = TwitterTools(bearer_token="your-token")
ipfs = IPFSTools(api_key="your-key", secret_key="your-secret")

def analyze_protocol_sentiment(protocol_name: str):
    # Collect tweets
    tweets = twitter.search_tweets(f"{protocol_name} protocol", limit=500)
    
    # Analyze sentiment
    sentiment = twitter.analyze_sentiment(tweets)
    
    # Identify influential voices
    influential_users = []
    for tweet in tweets[:50]:  # Top 50 tweets
        if tweet['author']['public_metrics']['followers_count'] > 10000:
            influence = twitter.analyze_user_influence(tweet['author']['username'])
            influential_users.append(influence)
    
    # Compile report
    report = {
        "protocol": protocol_name,
        "analysis_date": datetime.now().isoformat(),
        "tweet_count": len(tweets),
        "sentiment": sentiment,
        "influential_voices": influential_users[:10],  # Top 10
        "recommendations": generate_recommendations(sentiment)
    }
    
    # Store report on IPFS
    ipfs_hash = ipfs.upload_json(report, f"{protocol_name}-sentiment-report")
    print(f"Sentiment report stored: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
    
    return report

def generate_recommendations(sentiment_data):
    recommendations = []
    
    if sentiment_data['overall_sentiment'] < -0.3:
        recommendations.append("Consider community engagement to address concerns")
        recommendations.append("Review recent protocol changes for negative impact")
    
    if sentiment_data['positive_ratio'] > 0.7:
        recommendations.append("Leverage positive sentiment for marketing campaigns")
        recommendations.append("Consider expanding successful initiatives")
    
    return recommendations

# Analyze multiple protocols
protocols = ["Compound", "Aave", "Uniswap"]
for protocol in protocols:
    report = analyze_protocol_sentiment(protocol)
    print(f"{protocol} overall sentiment: {report['sentiment']['overall_sentiment']:.2f}")
```

### Secure Data Management

```python
from talos.tools.crypto import CryptographyTools
from talos.tools.ipfs import IPFSTools

# Set up tools
crypto = CryptographyTools()
ipfs = IPFSTools(api_key="your-key", secret_key="your-secret")

def secure_proposal_storage(proposal_data: dict):
    # Generate keys if needed
    if not crypto.get_public_key():
        private_key, public_key = crypto.generate_key_pair(2048)
        print(f"Generated new key pair: {public_key}")
    
    # Encrypt sensitive data
    sensitive_fields = ["financial_impact", "implementation_details"]
    encrypted_data = proposal_data.copy()
    
    for field in sensitive_fields:
        if field in encrypted_data:
            encrypted_value = crypto.encrypt_data(
                str(encrypted_data[field]),
                crypto.get_public_key()
            )
            encrypted_data[f"{field}_encrypted"] = encrypted_value
            del encrypted_data[field]
    
    # Sign the proposal
    proposal_text = json.dumps(encrypted_data, sort_keys=True)
    signature = crypto.sign_data(proposal_text)
    encrypted_data["signature"] = signature
    
    # Store on IPFS
    ipfs_hash = ipfs.upload_json(encrypted_data, "secure-proposal")
    
    return {
        "ipfs_hash": ipfs_hash,
        "public_key_fingerprint": crypto.get_key_fingerprint(),
        "encrypted_fields": sensitive_fields
    }

# Example usage
proposal = {
    "title": "Treasury Rebalancing Proposal",
    "description": "Proposal to rebalance treasury allocation",
    "financial_impact": {"amount": 1000000, "risk_level": "medium"},
    "implementation_details": {"timeline": "30 days", "steps": ["step1", "step2"]},
    "voting_period": "7 days"
}

result = secure_proposal_storage(proposal)
print(f"Secure proposal stored: {result['ipfs_hash']}")
```

## Error Handling

All tools include comprehensive error handling:

```python
from talos.tools.exceptions import ToolError, APIError, AuthenticationError

try:
    result = tool.execute(*args, **kwargs)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle token refresh or re-authentication
except APIError as e:
    print(f"API error: {e}")
    if e.status_code == 429:
        # Handle rate limiting
        time.sleep(60)
        result = tool.execute(*args, **kwargs)
except ToolError as e:
    print(f"Tool execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Rate Limiting

Tools automatically handle API rate limits:
- **GitHub**: 5000 requests/hour, automatic backoff
- **Twitter**: 300 requests/15 minutes, intelligent queuing
- **IPFS**: No strict limits, but connection pooling used

### Caching

Tools implement intelligent caching:
- **Repository data**: 5-minute cache
- **User profiles**: 1-hour cache
- **Sentiment analysis**: 30-minute cache for same queries

### Batch Operations

Many tools support batch operations for efficiency:

```python
# Batch GitHub operations
prs_to_review = [123, 124, 125, 126]
reviews = github.batch_review_pull_requests("owner", "repo", prs_to_review)

# Batch Twitter analysis
queries = ["DeFi", "yield farming", "staking", "governance"]
sentiment_results = twitter.batch_sentiment_analysis(queries, limit=100)
```

This tools API provides the external integration layer for Talos, enabling sophisticated interactions with GitHub, Twitter, IPFS, and cryptographic operations while maintaining security through supervised execution.
