# Theme Classification Architecture - Insight-Driven Agent (Pillar B)

## Overview

The Theme Classification system analyzes customer reviews (M2) to generate a Weekly Product Pulse, extracting top themes with confidence scores and sentiment analysis. These themes inform the Voice Agent's contextual awareness.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PILLAR B ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  WEEKLY PRODUCT PULSE GENERATOR (M2)                    ││
│  │  Input: Customer Reviews CSV                            ││
│  │  Output: Structured JSON                                ││
│  │  {                                                      ││
│  │    "top_themes": ["Login Issues", "Nominee Updates"],  ││
│  │    "sentiment_score": -0.3,                             ││
│  │    "action_ideas": ["...", "...", "..."],              ││
│  │    "word_count": 235                                    ││
│  │  }                                                      ││
│  └────────────────────────┬────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  THEME STORE (Shared State)                            ││
│  │  • Persisted in app state (LocalStorage/Redux)        ││
│  │  • Accessible across all pillars                       ││
│  └────────────────────────┬────────────────────────────────┘│
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  THEME-AWARE VOICE AGENT (M3)                            ││
│  │  ┌──────────────┐  ┌──────────────────────────────────┐││
│  │  │  Greeting    │  │  "I see many users are asking   │││
│  │  │  Generator   │  │   about {top_theme} today..."  │││
│  │  │  (Dynamic)   │  │                                  │││
│  │  └──────────────┘  └──────────────────────────────────┘││
│  │                                                          ││
│  │  Logic: IF top_theme.confidence > 0.7                  ││
│  │         THEN inject theme mention in greeting            ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### Theme Extraction Pipeline
1. **Groq (LLaMA 3)** extracts themes with confidence scores from reviews CSV
2. **scikit-learn TF-IDF + K-means** for theme clustering
3. **Sentiment analysis** per theme using TextBlob/vaderSentiment

### Structured Pulse Output
Groq LLM returns JSON with validation:
```json
{
  "top_themes": [
    {"theme": "Login Issues", "confidence": 0.85, "mention_count": 23},
    {"theme": "Nominee Updates", "confidence": 0.78, "mention_count": 18}
  ],
  "sentiment_score": -0.3,
  "action_ideas": ["...", "...", "..."],
  "word_count": 235
}
```

### Confidence Thresholding
Only themes with `confidence >= 0.7` trigger Voice Agent greeting modification.

### Dynamic Prompt Injection
Voice Agent greeting template uses Jinja2:
```python
greeting_template = """
{% if top_theme and top_theme.confidence >= 0.7 %}
Hello! I see many users are asking about {{ top_theme.theme }} today. 
I can help you book a call to discuss this!
{% else %}
Hello! How can I help you schedule a meeting today?
{% endif %}
"""
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Review Analysis** | Groq LLaMA 3 + Pandas + scikit-learn | Theme extraction with confidence scoring, sentiment analysis |
| **Theme Clustering** | scikit-learn TF-IDF + K-means | Unsupervised grouping of similar reviews |
| **Sentiment Analysis** | TextBlob / vaderSentiment | Rule-based sentiment scoring per theme |
| **Template Engine** | Jinja2 | Dynamic greeting generation |
| **Visualization** | Matplotlib / Plotly / Chart.js | Theme distribution, sentiment trends, mention volume charts |

## Analytics Dashboard

The UI includes an **Analytics Dashboard** (right panel) that visualizes:

- **Theme Distribution**: Pie chart showing proportion of each theme
- **Sentiment Trends**: Line graph showing week-over-week sentiment changes
- **Mention Volume**: Bar chart showing frequency of each theme mention
- **Keyword Cloud**: Word cloud visualization of top keywords

See [wireframe.md](wireframe.md) for the 2-column layout with analytics panel.

## Analytics Dashboard API

**API Endpoints** (supports `wireframe.md` Pillar B - Analytics Dashboard):

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/pillar-b/analytics` | GET | Full analytics dashboard data | `{pie_data, line_data, bar_data, keywords}` |
| `/api/pillar-b/analytics/themes` | GET | Theme distribution for pie chart | `[{theme, count, percentage}]` |
| `/api/pillar-b/analytics/sentiment` | GET | Sentiment trends for line graph | `[{date, sentiment_score}]` |
| `/api/pillar-b/analytics/volume` | GET | Mention volume for bar chart | `[{week, count}]` |
| `/api/pillar-b/analytics/keywords` | GET | Top keywords for cloud | `[{word, frequency}]` |

**Example**:
```python
# Get analytics dashboard data
GET /api/pillar-b/analytics
Response: {
  "theme_distribution": [
    {"theme": "Login Issues", "count": 45, "percentage": 35},
    {"theme": "Navigation", "count": 30, "percentage": 23},
    {"theme": "Performance", "count": 25, "percentage": 19}
  ],
  "sentiment_trends": [
    {"date": "2024-01-15", "score": 0.65},
    {"date": "2024-01-16", "score": 0.72}
  ],
  "mention_volume": [
    {"week": "W1", "count": 120},
    {"week": "W2", "count": 95}
  ],
  "keywords": [
    {"word": "login", "frequency": 42},
    {"word": "slow", "frequency": 28}
  ]
}
```

## Implementation

### Theme Extraction

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def extract_themes(reviews_csv: str) -> List[Theme]:
    """Extract themes from customer reviews."""
    # Load reviews
    df = pd.read_csv(reviews_csv)
    
    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(df['review_text'])
    
    # K-means clustering
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(X)
    
    # GPT-4o theme extraction from clusters
    themes = []
    for cluster_id in range(5):
        cluster_reviews = df[clusters == cluster_id]['review_text'].tolist()
        theme = gpt4o_extract_theme(cluster_reviews)
        themes.append(theme)
    
    return themes

def analyze_sentiment(texts: List[str]) -> float:
    """Calculate average sentiment score."""
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(t)['compound'] for t in texts]
    return sum(scores) / len(scores)
```

### Weekly Pulse Generation

```python
def generate_weekly_pulse(themes: List[Theme]) -> WeeklyPulse:
    """Generate structured Weekly Product Pulse."""
    # Sort by confidence
    top_themes = sorted(themes, key=lambda x: x.confidence, reverse=True)[:3]
    
    # Generate action ideas
    action_ideas = gpt4o_generate_actions(top_themes)
    
    # Compile pulse
    pulse = WeeklyPulse(
        top_themes=top_themes,
        sentiment_score=analyze_sentiment(themes),
        action_ideas=action_ideas[:3],  # Exactly 3
        word_count=0
    )
    
    # Validate word count < 250
    pulse.word_count = count_words(pulse.to_text())
    
    return pulse
```

## API Specification

```python
class ThemeStoreAPI:
    def get_current_themes(self) -> List[Theme]:
        """Returns top themes from latest Weekly Pulse"""
    
    def refresh_pulse(self, reviews_csv: str) -> WeeklyPulse:
        """Regenerates pulse from new review data"""
        
class Theme:
    theme: str
    confidence: float  # 0.0 - 1.0
    mention_count: int
    sentiment_score: float
    
class WeeklyPulse:
    top_themes: List[Theme]
    sentiment_score: float
    action_ideas: List[str]  # Exactly 3
    word_count: int  # Must be < 250
```

## Session State

```javascript
// Frontend State (LocalStorage/Redux)
const appState = {
    "weekly_pulse": {
        "generated_at": timestamp,
        "top_themes": [],
        "sentiment_score": float,
        "action_ideas": [],
        "raw_reviews_processed": int
    },
    "theme_last_updated": timestamp,
}
```

## Project Structure

```
src/pillar_b/
├── __init__.py
├── review_analyzer.py    # Theme extraction
├── pulse_generator.py    # Weekly Pulse creator
├── theme_store.py        # Shared state manager
└── voice_optimizer.py    # Greeting generator
```

## Dependencies

```txt
# Data Processing
pandas>=2.2.0
numpy>=1.26.0
scikit-learn>=1.5.0

# NLP & Sentiment
vaderSentiment>=3.3.0
jinja2>=3.1.0
textblob>=0.17.0

# Data Fetching
google-play-scraper>=1.2.4  # Play Store reviews
```

## Evaluation Rubric

| Criteria | Target | Measurement |
|----------|--------|-------------|
| **Word count** | ≤ 250 | Token count validation |
| **Action ideas** | Exactly 3 | Array length check |
| **Theme confidence** | > 0.7 | Threshold validation |
| **Theme propagation** | 100% | Voice agent mentions top theme |

---

## Weekly Pulse Sync Scheduler Architecture

### Data Source: Google Play Store

**INDMoney App**: `https://play.google.com/store/apps/details?id=in.indwealth&hl=en_IN`

Sample review data structure (`data/reviews/YYYY-MM-DD.json`):
```json
[
  {
    "reviewId": "r4",
    "rating": 3,
    "text": "Technical chart was better before. The new chart is not as user friendly...",
    "date": "2026-02-25T23:11:43",
    "userName": "[REDACTED]",
    "appVersion": "3.2.1"
  }
]
```

### GitHub Actions Weekly Cron

**Workflow** (`.github/workflows/fetch-reviews-weekly.yml`):
```yaml
name: Fetch Play Store Reviews Weekly

on:
  schedule:
    # Run every Sunday at 3:00 AM UTC (after RAG fund sync at 2:00 AM)
    - cron: '0 3 * * 0'
  workflow_dispatch:  # Manual trigger

jobs:
  fetch-and-analyze:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install google-play-scraper pandas scikit-learn vaderSentiment
      
      - name: Fetch INDMoney reviews
        run: |
          python scripts/fetch_playstore_reviews.py \
            --app-id in.indwealth \
            --output data/reviews/$(date +%Y-%m-%d).json \
            --count 100  # Last 100 reviews
      
      - name: Generate Weekly Pulse
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python pillar_b/pulse_generator.py \
            --reviews data/reviews/$(date +%Y-%m-%d).json \
            --output data/weekly_pulse.json
      
      - name: Update freshness timestamp
        run: |
          echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > data/last_pulse_sync.txt
      
      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/reviews/ data/weekly_pulse.json data/last_pulse_sync.txt
          git diff --quiet && git diff --staged --quiet || git commit -m "Weekly pulse: $(date +%Y-%m-%d)"
          git push
```

### Play Store Scraper Script

**`scripts/fetch_playstore_reviews.py`**:
```python
from google_play_scraper import reviews, Sort
import json
import argparse
from datetime import datetime

def fetch_reviews(app_id: str, count: int = 100, lang: str = 'en', country: str = 'in'):
    """Fetch reviews from Google Play Store."""
    
    result, _ = reviews(
        app_id,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=count,
        filter_score_with=None  # All ratings
    )
    
    # Transform to internal format with PII redaction
    formatted_reviews = []
    for r in result:
        formatted_reviews.append({
            "reviewId": r['reviewId'],
            "rating": r['score'],
            "text": r['content'],
            "date": r['at'].isoformat() if r['at'] else None,
            "userName": "[REDACTED]",  # PII protection
            "appVersion": r['reviewCreatedVersion']
        })
    
    return formatted_reviews

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app-id', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--count', type=int, default=100)
    args = parser.parse_args()
    
    reviews_data = fetch_reviews(args.app_id, args.count)
    
    with open(args.output, 'w') as f:
        json.dump(reviews_data, f, indent=2)
    
    print(f"✓ Fetched {len(reviews_data)} reviews to {args.output}")

if __name__ == "__main__":
    main()
```

### Schedule Coordination with Pillar A (RAG)

| Time (UTC) | Day | Job | Duration |
|------------|-----|-----|----------|
| 2:00 AM | Sunday | RAG fund data sync | ~5 min |
| 3:00 AM | Sunday | M2 review fetch + pulse generation | ~3 min |

---

## Pulse Freshness Indicator

### Backend: Expose Pulse Metadata

```python
from datetime import datetime
from pathlib import Path

def get_pulse_freshness() -> dict:
    """Get weekly pulse freshness metadata."""
    last_sync_file = Path("data/last_pulse_sync.txt")
    pulse_file = Path("data/weekly_pulse.json")
    
    if last_sync_file.exists() and pulse_file.exists():
        last_sync = last_sync_file.read_text().strip()
        last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
        days_since = (datetime.utcnow() - last_sync_dt).days
        
        # Load current pulse for theme display
        with open(pulse_file) as f:
            pulse = json.load(f)
        
        status = "fresh" if days_since <= 7 else "stale" if days_since <= 14 else "outdated"
        
        return {
            "last_pulse_generated": last_sync,
            "days_since_pulse": days_since,
            "status": status,
            "reviews_analyzed": len(pulse.get("raw_reviews", [])),
            "top_theme": pulse.get("top_themes", [{}])[0].get("theme", "None"),
            "sentiment_score": pulse.get("sentiment_score", 0),
            "next_scheduled_sync": get_next_cron_date("0 3 * * 0").isoformat()
        }
    
    return {
        "last_pulse_generated": None,
        "days_since_pulse": None,
        "status": "unknown",
        "top_theme": "None",
        "reviews_analyzed": 0
    }
```

### Frontend: Pulse Status Badge

**React Component**:
```jsx
const PulseFreshnessBadge = ({ freshness }) => {
  if (!freshness?.last_pulse_generated) return null;
  
  const { status, days_since_pulse, top_theme, reviews_analyzed } = freshness;
  
  const statusConfig = {
    fresh: { color: '#10B981', emoji: '🟢', text: 'Pulse current' },
    stale: { color: '#F59E0B', emoji: '🟡', text: 'Pulse 1-2 weeks old' },
    outdated: { color: '#EF4444', emoji: '🔴', text: 'Pulse >2 weeks old' },
    unknown: { color: '#6B7280', emoji: '⚪', text: 'Pulse status unknown' }
  };
  
  const config = statusConfig[status] || statusConfig.unknown;
  
  return (
    <div className="pulse-freshness-badge" style={{ borderColor: config.color }}>
      <span style={{ color: config.color }}>{config.emoji}</span>
      <span className="pulse-text">{config.text}</span>
      <span className="pulse-detail">
        Top theme: <strong>{top_theme}</strong> | 
        {reviews_analyzed} reviews | 
        {days_since_pulse === 0 ? 'Today' : `${days_since_pulse} days ago`}
      </span>
    </div>
  );
};
```

**CSS Styles**:
```css
.pulse-freshness-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-left: 3px solid;
  background: #f0f9ff;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.pulse-text {
  font-weight: 600;
}

.pulse-detail {
  color: #4b5563;
  font-size: 0.85rem;
  margin-left: auto;
}
```

### Pulse Status States

| Status | Days Since Pulse | Color | Action |
|--------|-----------------|-------|--------|
| 🟢 **Fresh** | ≤ 7 days | Green | None |
| 🟡 **Stale** | 8-14 days | Amber | Show warning |
| 🔴 **Outdated** | > 14 days | Red | Manual refresh button |
| ⚪ **Unknown** | No pulse generated | Gray | Show "Generate Pulse" button |

---

## Testing Checklist

- [ ] Play Store review fetcher configured (weekly cron)
- [ ] Review data includes: reviewId, rating, text, date
- [ ] PII redaction applied (userName → [REDACTED])
- [ ] Weekly Pulse freshness indicator displays "Last generated" timestamp
- [ ] Pulse generator runs after review fetch completes
- [ ] Theme extraction identifies top 3 themes with confidence scores
- [ ] Sentiment analysis produces score between -1 and +1
- [ ] Word count validation enforces ≤ 250 words
- [ ] Action ideas array contains exactly 3 items
- [ ] Voice Agent greeting incorporates top theme when confidence ≥ 0.7

---

## References

1. [TF-IDF Vectorization](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
2. [K-Means Clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
3. [VADER Sentiment](https://github.com/cjhutto/vaderSentiment)
