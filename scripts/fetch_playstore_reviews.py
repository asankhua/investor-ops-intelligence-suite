#!/usr/bin/env python3
"""Fetch Google Play Store reviews for INDMoney app."""

from google_play_scraper import reviews, Sort
import json
import argparse
from datetime import datetime
from pathlib import Path

def fetch_reviews(app_id: str, count: int = 100, lang: str = 'en', country: str = 'in'):
    """Fetch reviews from Google Play Store."""
    
    print(f"Fetching {count} reviews for app: {app_id}")
    
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
    parser.add_argument('--app-id', default='in.indwealth', help='Play Store app ID')
    parser.add_argument('--output', help='Output JSON file')
    parser.add_argument('--count', type=int, default=100, help='Number of reviews')
    args = parser.parse_args()
    
    # Default output path if not provided
    if not args.output:
        today = datetime.now().strftime('%Y-%m-%d')
        args.output = f'data/reviews/{today}.json'
    
    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Fetch reviews
    reviews_data = fetch_reviews(args.app_id, args.count)
    
    # Save to file
    with open(args.output, 'w') as f:
        json.dump(reviews_data, f, indent=2)
    
    print(f"✓ Fetched {len(reviews_data)} reviews to {args.output}")
    
    # Print summary
    ratings = [r['rating'] for r in reviews_data]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    print(f"  Average rating: {avg_rating:.1f}/5")
    print(f"  Date range: {reviews_data[-1]['date'][:10] if reviews_data else 'N/A'} to {reviews_data[0]['date'][:10] if reviews_data else 'N/A'}")

if __name__ == "__main__":
    main()
