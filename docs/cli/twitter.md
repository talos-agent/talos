# Twitter Commands

The Talos CLI provides comprehensive Twitter integration for sentiment analysis, community monitoring, and social media engagement.

## Setup

### Authentication

Set your Twitter Bearer Token as an environment variable:

```bash
export TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### API Access

Twitter commands require:
- Twitter API v2 access
- Bearer Token with read permissions
- Rate limiting awareness (300 requests per 15 minutes)

## Commands

### `get-user-prompt` - User Voice Analysis

Analyze a Twitter user's general voice and communication style to generate a prompt that captures their personality.

**Usage:**
```bash
uv run talos twitter get-user-prompt <username>
```

**Arguments:**
- `username`: Twitter username (without @ symbol)

**Examples:**
```bash
# Analyze a specific user's communication style
uv run talos twitter get-user-prompt elonmusk

# Analyze multiple users
uv run talos twitter get-user-prompt vitalikbuterin
uv run talos twitter get-user-prompt naval
```

**Output:**
```
=== User Voice Analysis: @elonmusk ===

Communication Style:
- Direct and concise messaging
- Technical depth with accessible explanations
- Frequent use of humor and memes
- Bold predictions and statements
- Engineering-focused perspective

Key Themes:
- Technology and innovation
- Space exploration and Mars colonization
- Electric vehicles and sustainable energy
- AI development and safety
- Manufacturing and production efficiency

Tone Characteristics:
- Confident and assertive
- Occasionally provocative
- Optimistic about technology
- Critical of bureaucracy
- Supportive of free speech

Generated Prompt:
"Communicate with the direct, confident style of a tech innovator. 
Be concise but technically accurate. Use accessible language to 
explain complex concepts. Show optimism about technological 
progress while being realistic about challenges. Occasionally 
use humor to make points more memorable."
```

### `get-query-sentiment` - Sentiment Analysis

Analyze sentiment around specific topics, keywords, or phrases on Twitter.

**Usage:**
```bash
uv run talos twitter get-query-sentiment "<query>"
```

**Arguments:**
- `query`: Search query or topic to analyze

**Options:**
- `--limit`: Number of tweets to analyze (default: 100, max: 1000)
- `--days`: Number of days to look back (default: 7, max: 30)
- `--lang`: Language filter (default: en)

**Examples:**
```bash
# Basic sentiment analysis
uv run talos twitter get-query-sentiment "DeFi yield farming"

# Extended analysis with more tweets
uv run talos twitter get-query-sentiment "Ethereum staking" --limit 500

# Recent sentiment (last 24 hours)
uv run talos twitter get-query-sentiment "crypto market" --days 1

# Multi-language analysis
uv run talos twitter get-query-sentiment "Bitcoin" --lang all
```

**Output:**
```
=== Sentiment Analysis: "DeFi yield farming" ===

Overall Sentiment: MIXED (Slightly Positive)
Confidence: 78%

Sentiment Distribution:
🟢 Positive: 45% (450 tweets)
🟡 Neutral:  32% (320 tweets)  
🔴 Negative: 23% (230 tweets)

Key Themes:
Positive Sentiments:
- High APY opportunities (mentioned 156 times)
- New protocol launches (mentioned 89 times)
- Successful farming strategies (mentioned 67 times)

Negative Sentiments:
- Impermanent loss concerns (mentioned 78 times)
- Rug pull warnings (mentioned 45 times)
- Gas fee complaints (mentioned 34 times)

Influential Voices:
@defi_analyst (50k followers): "Yield farming still profitable with right strategy"
@crypto_researcher (25k followers): "Be careful of new farms, many are unsustainable"

Trending Hashtags:
#DeFi (mentioned 234 times)
#YieldFarming (mentioned 189 times)
#APY (mentioned 156 times)

Recommendations:
- Monitor impermanent loss discussions for user concerns
- Address gas fee issues in communications
- Highlight sustainable yield strategies
- Engage with influential voices sharing positive content
```

## Advanced Usage

### Sentiment Monitoring

Set up continuous monitoring for important topics:

```bash
#!/bin/bash
# sentiment-monitor.sh

topics=("our_protocol" "DeFi governance" "yield farming" "staking rewards")

for topic in "${topics[@]}"; do
  echo "Monitoring: $topic"
  uv run talos twitter get-query-sentiment "$topic" --limit 200
  echo "---"
done
```

### Competitor Analysis

Monitor sentiment around competitor protocols:

```bash
#!/bin/bash
# competitor-sentiment.sh

competitors=("Compound" "Aave" "Uniswap" "SushiSwap")

for competitor in "${competitors[@]}"; do
  echo "=== $competitor Sentiment ==="
  uv run talos twitter get-query-sentiment "$competitor protocol" --limit 300
  echo ""
done
```

### Influencer Tracking

Analyze key influencers in your space:

```bash
#!/bin/bash
# influencer-analysis.sh

influencers=("vitalikbuterin" "haydenzadams" "stanikulechov" "rleshner")

for influencer in "${influencers[@]}"; do
  echo "=== @$influencer Analysis ==="
  uv run talos twitter get-user-prompt "$influencer"
  echo ""
done
```

## Integration with Protocol Management

### APR Adjustment Based on Sentiment

```bash
#!/bin/bash
# apr-sentiment-adjustment.sh

# Get current sentiment about yield farming
sentiment=$(uv run talos twitter get-query-sentiment "yield farming APR" --format=json)

# Extract sentiment score
score=$(echo $sentiment | jq '.sentiment_score')

# Adjust APR based on sentiment
if [ $score -gt 0.7 ]; then
  echo "Positive sentiment detected. Consider maintaining or slightly increasing APR."
elif [ $score -lt 0.3 ]; then
  echo "Negative sentiment detected. Consider increasing APR to attract users."
else
  echo "Neutral sentiment. Monitor closely for changes."
fi
```

### Community Response Strategy

```bash
#!/bin/bash
# community-response.sh

# Monitor mentions of our protocol
mentions=$(uv run talos twitter get-query-sentiment "our_protocol_name" --limit 500)

# Check for negative sentiment spikes
negative_ratio=$(echo $mentions | jq '.negative_ratio')

if [ $(echo "$negative_ratio > 0.4" | bc) -eq 1 ]; then
  echo "High negative sentiment detected!"
  echo "Recommended actions:"
  echo "1. Investigate main concerns"
  echo "2. Prepare community response"
  echo "3. Consider protocol adjustments"
  
  # Get specific concerns
  uv run talos twitter get-query-sentiment "our_protocol_name problems" --limit 100
fi
```

## Configuration

### Rate Limiting

Configure rate limiting to respect Twitter API limits:

```yaml
twitter:
  rate_limiting:
    requests_per_window: 300
    window_minutes: 15
    backoff_strategy: "exponential"
    
  analysis:
    default_tweet_limit: 100
    max_tweet_limit: 1000
    default_days_back: 7
    max_days_back: 30
```

### Sentiment Thresholds

Configure sentiment analysis thresholds:

```yaml
twitter:
  sentiment:
    positive_threshold: 0.6
    negative_threshold: 0.4
    confidence_threshold: 0.7
    
  alerts:
    negative_spike_threshold: 0.5
    volume_spike_threshold: 200
    influencer_mention_threshold: 10000  # follower count
```

## Error Handling

### Common Issues

**Rate Limiting:**
```
Error: Rate limit exceeded
Solution: Wait 15 minutes or reduce query frequency
```

**Invalid Bearer Token:**
```
Error: Twitter API authentication failed
Solution: Check TWITTER_BEARER_TOKEN environment variable
```

**No Results:**
```
Warning: No tweets found for query "very_specific_term"
Solution: Try broader search terms or increase time range
```

**API Quota Exceeded:**
```
Error: Monthly API quota exceeded
Solution: Upgrade Twitter API plan or wait for quota reset
```

### Automatic Handling

Talos automatically handles:
- **Rate Limiting** - Waits and retries when limits are reached
- **Network Errors** - Retries with exponential backoff
- **Partial Results** - Returns available data when some requests fail
- **Invalid Queries** - Suggests alternative search terms

## Best Practices

### Effective Queries

**Use Specific Terms:**
```bash
# Good: Specific and relevant
uv run talos twitter get-query-sentiment "Ethereum staking rewards"

# Poor: Too broad
uv run talos twitter get-query-sentiment "crypto"
```

**Include Context:**
```bash
# Good: Includes protocol context
uv run talos twitter get-query-sentiment "Compound lending rates"

# Good: Includes sentiment context
uv run talos twitter get-query-sentiment "DeFi security concerns"
```

### Monitoring Strategy

**Regular Monitoring:**
- Daily sentiment checks for your protocol
- Weekly competitor analysis
- Monthly influencer voice updates

**Alert-Based Monitoring:**
- Set up alerts for negative sentiment spikes
- Monitor for unusual volume increases
- Track mentions by high-influence accounts

### Data Interpretation

**Consider Context:**
- Market conditions affect overall sentiment
- News events can cause temporary sentiment shifts
- Bot activity may skew results

**Look for Trends:**
- Focus on sentiment trends over time
- Compare relative sentiment between topics
- Identify recurring themes and concerns

**Validate Insights:**
- Cross-reference with other data sources
- Verify with community feedback
- Test sentiment-based decisions carefully

The Twitter integration provides powerful tools for understanding community sentiment and making data-driven decisions about protocol management and community engagement.
