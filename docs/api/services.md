# Services API Reference

This document provides detailed API reference for the services layer of the Talos system.

## Base Service Interface

### Service

Abstract base class for all services in the Talos system.

```python
from abc import ABC, abstractmethod

class Service(ABC):
    @abstractmethod
    def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process a service request and return response."""
        pass
```

## Service Models

### ServiceRequest

Base request model for all service operations.

```python
class ServiceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)
```

### ServiceResponse

Base response model for all service operations.

```python
class ServiceResponse(BaseModel):
    request_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    processing_time: Optional[float] = None
```

## Yield Management Services

### YieldManagerService

Calculates optimal staking APR using market data and sentiment analysis.

```python
class YieldManagerService(Service):
    def __init__(self, model: str = "gpt-5"):
        """Initialize yield manager service.
        
        Args:
            model: LLM model to use for analysis
        """
```

#### Methods

##### `process(request: YieldManagerRequest) -> YieldManagerResponse`

Calculate optimal APR based on market conditions and sentiment.

**Parameters:**
- `request` (YieldManagerRequest): Request containing market data and parameters

**Returns:**
- `YieldManagerResponse`: Response with recommended APR and analysis

**Example:**
```python
from talos.services.yield_manager import YieldManagerService, YieldManagerRequest

service = YieldManagerService()
request = YieldManagerRequest(
    current_apr=0.05,
    market_volatility=0.15,
    competitor_aprs=[0.06, 0.07, 0.055],
    sentiment_score=0.7,
    tvl=1000000,
    utilization_rate=0.8
)

response = service.process(request)
print(f"Recommended APR: {response.recommended_apr}")
print(f"Reasoning: {response.reasoning}")
```

### YieldManagerRequest

Request model for yield management operations.

```python
class YieldManagerRequest(ServiceRequest):
    current_apr: float = Field(ge=0.0, le=1.0)
    market_volatility: float = Field(ge=0.0)
    competitor_aprs: List[float] = Field(default_factory=list)
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    tvl: float = Field(ge=0.0)
    utilization_rate: float = Field(ge=0.0, le=1.0)
    risk_tolerance: str = Field(default="medium")  # low, medium, high
```

### YieldManagerResponse

Response model for yield management operations.

```python
class YieldManagerResponse(ServiceResponse):
    recommended_apr: float
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    risk_assessment: str
    market_analysis: dict
    implementation_timeline: str
```

## Sentiment Analysis Services

### TalosSentimentService

Orchestrates comprehensive sentiment analysis across multiple data sources.

```python
class TalosSentimentService(Service):
    def __init__(self):
        """Initialize sentiment analysis service."""
```

#### Methods

##### `process(request: SentimentRequest) -> SentimentResponse`

Perform comprehensive sentiment analysis.

**Parameters:**
- `request` (SentimentRequest): Request with query and analysis parameters

**Returns:**
- `SentimentResponse`: Comprehensive sentiment analysis results

**Example:**
```python
from talos.services.sentiment import TalosSentimentService, SentimentRequest

service = TalosSentimentService()
request = SentimentRequest(
    query="DeFi yield farming",
    sources=["twitter", "reddit", "discord"],
    limit=500,
    days_back=7
)

response = service.process(request)
print(f"Overall sentiment: {response.overall_sentiment}")
print(f"Confidence: {response.confidence}")
for theme in response.key_themes:
    print(f"Theme: {theme.topic} - Sentiment: {theme.sentiment}")
```

### SentimentRequest

Request model for sentiment analysis operations.

```python
class SentimentRequest(ServiceRequest):
    query: str = Field(min_length=1, max_length=500)
    sources: List[str] = Field(default=["twitter"])
    limit: int = Field(default=100, ge=1, le=1000)
    days_back: int = Field(default=7, ge=1, le=30)
    language: str = Field(default="en")
    include_influencers: bool = Field(default=True)
```

### SentimentResponse

Response model for sentiment analysis operations.

```python
class SentimentResponse(ServiceResponse):
    overall_sentiment: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    sentiment_distribution: dict  # positive, neutral, negative percentages
    key_themes: List[SentimentTheme]
    influential_voices: List[InfluentialVoice]
    trending_hashtags: List[str]
    recommendations: List[str]
    data_sources: dict  # source -> count mapping
```

### SentimentTheme

Individual sentiment theme with associated metrics.

```python
class SentimentTheme(BaseModel):
    topic: str
    sentiment: float = Field(ge=-1.0, le=1.0)
    mention_count: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)
    examples: List[str] = Field(default_factory=list)
```

### InfluentialVoice

Influential account or voice in sentiment analysis.

```python
class InfluentialVoice(BaseModel):
    username: str
    platform: str
    follower_count: int = Field(ge=0)
    sentiment: float = Field(ge=-1.0, le=1.0)
    influence_score: float = Field(ge=0.0, le=1.0)
    recent_content: str
```

## GitHub Services

### GithubService

Handles GitHub operations including repository management and PR reviews.

```python
class GithubService(Service):
    def __init__(self, token: str):
        """Initialize GitHub service.
        
        Args:
            token: GitHub API token
        """
```

#### Methods

##### `process(request: GithubRequest) -> GithubResponse`

Process GitHub operations based on request type.

**Parameters:**
- `request` (GithubRequest): Request specifying the GitHub operation

**Returns:**
- `GithubResponse`: Response with operation results

**Example:**
```python
from talos.services.github import GithubService, GithubRequest

service = GithubService(token="your-github-token")

# Review a pull request
request = GithubRequest(
    operation="review_pr",
    repository="owner/repo",
    pr_number=123,
    auto_approve=False
)

response = service.process(request)
print(f"Security Score: {response.security_score}")
print(f"Quality Score: {response.quality_score}")
print(f"Recommendation: {response.recommendation}")
```

### GithubRequest

Request model for GitHub operations.

```python
class GithubRequest(ServiceRequest):
    operation: str  # "review_pr", "list_prs", "approve_pr", "merge_pr"
    repository: str
    pr_number: Optional[int] = None
    state: str = Field(default="open")  # open, closed, all
    auto_approve: bool = Field(default=False)
    post_review: bool = Field(default=False)
```

### GithubResponse

Response model for GitHub operations.

```python
class GithubResponse(ServiceResponse):
    operation: str
    repository: str
    pr_number: Optional[int] = None
    security_score: Optional[int] = Field(ge=0, le=100)
    quality_score: Optional[int] = Field(ge=0, le=100)
    recommendation: Optional[str] = None
    detailed_analysis: Optional[str] = None
    pull_requests: Optional[List[dict]] = None
```

## Usage Examples

### Comprehensive Yield Optimization

```python
from talos.services.yield_manager import YieldManagerService, YieldManagerRequest
from talos.services.sentiment import TalosSentimentService, SentimentRequest

# Get sentiment data
sentiment_service = TalosSentimentService()
sentiment_request = SentimentRequest(
    query="yield farming APR",
    sources=["twitter", "reddit"],
    limit=200
)
sentiment_response = sentiment_service.process(sentiment_request)

# Calculate optimal APR using sentiment data
yield_service = YieldManagerService()
yield_request = YieldManagerRequest(
    current_apr=0.05,
    market_volatility=0.12,
    competitor_aprs=[0.06, 0.07, 0.055],
    sentiment_score=sentiment_response.overall_sentiment,
    tvl=2000000,
    utilization_rate=0.75
)
yield_response = yield_service.process(yield_request)

print(f"Current sentiment: {sentiment_response.overall_sentiment}")
print(f"Recommended APR: {yield_response.recommended_apr}")
print(f"Reasoning: {yield_response.reasoning}")
```

### Automated PR Review Workflow

```python
from talos.services.github import GithubService, GithubRequest

service = GithubService(token="your-token")

# List open PRs
list_request = GithubRequest(
    operation="list_prs",
    repository="your-org/your-repo",
    state="open"
)
list_response = service.process(list_request)

# Review each PR
for pr in list_response.pull_requests:
    review_request = GithubRequest(
        operation="review_pr",
        repository="your-org/your-repo",
        pr_number=pr["number"],
        post_review=True,
        auto_approve=True
    )
    
    review_response = service.process(review_request)
    
    print(f"PR #{pr['number']}: {review_response.recommendation}")
    print(f"Security: {review_response.security_score}/100")
    print(f"Quality: {review_response.quality_score}/100")
```

### Multi-Source Sentiment Analysis

```python
from talos.services.sentiment import TalosSentimentService, SentimentRequest

service = TalosSentimentService()

# Analyze sentiment across multiple topics
topics = ["DeFi protocols", "yield farming", "staking rewards", "governance tokens"]
results = {}

for topic in topics:
    request = SentimentRequest(
        query=topic,
        sources=["twitter", "reddit"],
        limit=300,
        days_back=7
    )
    
    response = service.process(request)
    results[topic] = {
        "sentiment": response.overall_sentiment,
        "confidence": response.confidence,
        "themes": [theme.topic for theme in response.key_themes[:3]]
    }

# Analyze results
for topic, data in results.items():
    print(f"{topic}: {data['sentiment']:.2f} (confidence: {data['confidence']:.2f})")
    print(f"  Key themes: {', '.join(data['themes'])}")
```

## Error Handling

Services include comprehensive error handling for various failure scenarios:

```python
from talos.services.exceptions import ServiceError, APIError, ValidationError

try:
    response = service.process(request)
    if not response.success:
        print(f"Service error: {response.error}")
    else:
        # Process successful response
        print(f"Success: {response.data}")
        
except ValidationError as e:
    print(f"Invalid request: {e}")
except APIError as e:
    print(f"External API error: {e}")
except ServiceError as e:
    print(f"Service processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Caching

Services implement intelligent caching for frequently accessed data:

```python
# Sentiment analysis results are cached for 1 hour
# GitHub repository data is cached for 5 minutes
# Market data is cached for 30 seconds
```

### Rate Limiting

All services respect external API rate limits:

- **GitHub API**: 5000 requests per hour
- **Twitter API**: 300 requests per 15 minutes
- **OpenAI API**: Varies by plan

### Batch Operations

Services support batch operations for efficiency:

```python
# Batch sentiment analysis
batch_request = SentimentBatchRequest(
    queries=["topic1", "topic2", "topic3"],
    sources=["twitter"],
    limit=100
)
batch_response = sentiment_service.process_batch(batch_request)
```

This services API provides the business logic layer for Talos operations, enabling sophisticated protocol management through well-defined interfaces and comprehensive error handling.
