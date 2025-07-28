# Skills & Services

Talos uses a modular architecture with Skills and Services that provide specialized capabilities for different aspects of protocol management.

## Architecture Overview

### Skills vs Services

**Skills** are modular capabilities that can be directly invoked by users or other system components:
- User-facing functionality
- Direct query handling
- Standardized input/output interface
- Can be combined for complex workflows

**Services** are business logic implementations that provide domain-specific functionality:
- Backend processing logic
- Integration with external systems
- Can be used by multiple skills
- Focus on specific business domains

## Skills System

### Base Skill Interface

All skills inherit from the abstract `Skill` base class:

```python
class Skill:
    def run(self, **kwargs) -> QueryResponse:
        """Execute the skill with provided parameters"""
        pass
    
    def create_ticket_tool(self) -> BaseTool:
        """Create a tool for ticket-based execution"""
        pass
```

**Standard Interface:**
- **run()** method for direct execution
- **QueryResponse** return type for consistent output
- **create_ticket_tool()** for tool integration
- Parameter validation and type checking

### Available Skills

#### ProposalsSkill

Evaluates governance proposals using LLM analysis:

**Capabilities:**
- **Proposal Analysis** - Detailed evaluation of governance proposals
- **Risk Assessment** - Identify potential risks and benefits
- **Community Impact** - Assess impact on community and stakeholders
- **Recommendation Generation** - Provide clear approve/reject recommendations

**Usage:**
```python
skill = ProposalsSkill()
result = skill.run(proposal_text="Increase staking rewards by 10%")
```

**Output:**
- Detailed analysis report
- Risk/benefit assessment
- Community impact evaluation
- Clear recommendation with reasoning

#### TwitterSentimentSkill

Analyzes Twitter sentiment for given queries:

**Capabilities:**
- **Tweet Collection** - Gather relevant tweets for analysis
- **Sentiment Analysis** - Evaluate positive/negative sentiment
- **Trend Detection** - Identify emerging trends and topics
- **Influence Scoring** - Assess account influence and credibility

**Usage:**
```python
skill = TwitterSentimentSkill()
result = skill.run(query="DeFi yield farming", limit=100)
```

**Output:**
- Sentiment scores and distribution
- Key themes and topics
- Influential accounts and tweets
- Trend analysis and insights

#### TwitterInfluencerSkill

Evaluates Twitter accounts for crypto influence:

**Capabilities:**
- **Account Analysis** - Comprehensive account evaluation
- **Influence Scoring** - Multi-metric influence assessment
- **Content Analysis** - Evaluate tweet quality and relevance
- **Network Analysis** - Assess follower quality and engagement

**Metrics:**
- Follower count and growth
- Engagement rates
- Content quality scores
- Network influence metrics

#### CryptographySkill

Provides encryption and decryption operations:

**Capabilities:**
- **Key Generation** - RSA key pair generation
- **Encryption/Decryption** - Secure message handling
- **Digital Signatures** - Message signing and verification
- **Key Management** - Secure key storage and retrieval

**Security Features:**
- Industry-standard encryption algorithms
- Secure key storage
- Audit trail for all operations
- Integration with hardware security modules

#### ExecutionPlannerSkill

Generates execution plans for complex tasks:

**Capabilities:**
- **Task Decomposition** - Break complex tasks into steps
- **Dependency Analysis** - Identify task dependencies
- **Resource Planning** - Estimate required resources
- **Timeline Generation** - Create realistic execution timelines

**Use Cases:**
- Protocol upgrade planning
- Treasury rebalancing strategies
- Community engagement campaigns
- Development roadmap planning

## Services System

### Base Service Interface

Services implement the abstract `Service` interface:

```python
class Service:
    def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process a service request"""
        pass
```

### Available Services

#### YieldManagerService

Calculates optimal staking APR using market data and sentiment:

**Inputs:**
- Current market conditions
- Protocol metrics (TVL, utilization)
- Community sentiment data
- Competitor analysis

**Processing:**
- **Market Analysis** - Evaluate current DeFi landscape
- **Risk Assessment** - Assess protocol-specific risks
- **Sentiment Integration** - Factor in community sentiment
- **Optimization** - Calculate optimal APR using LLM reasoning

**Output:**
- Recommended APR with reasoning
- Risk assessment and mitigation strategies
- Market positioning analysis
- Implementation timeline

#### TalosSentimentService

Orchestrates comprehensive sentiment analysis:

**Workflow:**
1. **Data Collection** - Gather data from multiple sources
2. **Preprocessing** - Clean and normalize data
3. **Analysis** - Apply sentiment analysis algorithms
4. **Aggregation** - Combine results from different sources
5. **Reporting** - Generate actionable insights

**Data Sources:**
- Twitter and social media
- Discord and Telegram communities
- Reddit discussions
- News articles and blogs

#### GithubService

Handles GitHub operations and PR reviews:

**Capabilities:**
- **Repository Management** - Clone, fork, branch operations
- **Pull Request Reviews** - Automated code review and scoring
- **Issue Management** - Create, update, and track issues
- **Workflow Automation** - CI/CD integration and automation

**Review Process:**
1. **Code Analysis** - Static analysis and quality checks
2. **Security Scanning** - Vulnerability detection
3. **Style Validation** - Code style and convention checks
4. **Test Coverage** - Ensure adequate test coverage
5. **Documentation** - Verify documentation updates

## Router System

### Query Routing

The `Router` directs queries to appropriate skills and services:

```python
class Router:
    def __init__(self):
        self.skills = []
        self.services = []
        self.keyword_mapping = {}
    
    def route(self, query: str) -> Union[Skill, Service]:
        """Route query to appropriate handler"""
        pass
```

**Routing Logic:**
- **Keyword Matching** - Match query keywords to skills/services
- **Intent Recognition** - Understand user intent from query
- **Context Awareness** - Consider conversation history
- **Fallback Handling** - Default routing for unmatched queries

### Registration System

Skills and services are dynamically registered:

```python
# Skill registration
router.register_skill(ProposalsSkill(), keywords=["proposal", "governance"])
router.register_skill(TwitterSentimentSkill(), keywords=["sentiment", "twitter"])

# Service registration
router.register_service(YieldManagerService(), keywords=["yield", "apr", "staking"])
```

## Integration Patterns

### Skill Composition

Skills can be combined for complex workflows:

```python
class ComplexWorkflowSkill(Skill):
    def __init__(self):
        self.sentiment_skill = TwitterSentimentSkill()
        self.yield_service = YieldManagerService()
    
    def run(self, **kwargs):
        # Get sentiment data
        sentiment = self.sentiment_skill.run(query="protocol sentiment")
        
        # Calculate optimal yield
        yield_data = self.yield_service.process(sentiment_data=sentiment)
        
        return QueryResponse(answers=[yield_data])
```

### Service Orchestration

Services can orchestrate multiple operations:

```python
class ProtocolManagementService(Service):
    def process(self, request):
        # Analyze market conditions
        market_data = self.market_service.get_conditions()
        
        # Get community sentiment
        sentiment = self.sentiment_service.analyze()
        
        # Calculate optimal parameters
        params = self.optimization_service.optimize(market_data, sentiment)
        
        return ServiceResponse(recommendations=params)
```

## Best Practices

### Skill Development

- **Single Responsibility** - Each skill should have one clear purpose
- **Consistent Interface** - Follow the standard Skill interface
- **Error Handling** - Robust error handling and user feedback
- **Documentation** - Clear documentation of inputs and outputs

### Service Design

- **Stateless Operations** - Services should be stateless when possible
- **Idempotent Operations** - Operations should be safely repeatable
- **Resource Management** - Proper cleanup of external resources
- **Monitoring** - Comprehensive logging and metrics

### Integration Guidelines

- **Loose Coupling** - Minimize dependencies between components
- **Standard Interfaces** - Use consistent data formats and APIs
- **Error Propagation** - Proper error handling across component boundaries
- **Testing** - Comprehensive unit and integration testing

This modular architecture enables Talos to provide sophisticated protocol management capabilities while maintaining flexibility and extensibility for future enhancements.
