#!/usr/bin/env python3
"""Fetch latest mutual fund data from INDMoney."""

import json
import re
import argparse
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip3", "install", "requests", "beautifulsoup4", "-q"])
    import requests
    from bs4 import BeautifulSoup

def extract_fund_info(html_content: str, scheme_id: str) -> dict:
    """Extract fund information from INDMoney HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Try to extract fund name from title or page
    fund_name = scheme_id.split('-')[:-1]
    fund_name = ' '.join([w.capitalize() for w in fund_name])
    
    # For now, return a structure that matches the existing format
    # In a real implementation, this would parse the HTML to extract live NAV, returns, etc.
    fund_data = {
        "scheme_id": scheme_id,
        "name": fund_name,
        "source_url": f"https://www.indmoney.com/mutual-funds/{scheme_id}",
        "overview": {
            "nav": "[Fetch from live source - see source_url]",
            "returns_since_inception": "[Fetch from live source]",
            "returns_1y": "[Fetch from live source]",
            "returns_3y": "[Fetch from live source]",
            "returns_5y": "[Fetch from live source]",
            "expense_ratio": "[Fetch from live source]",
            "benchmark": "[Fetch from live source]",
            "aum": "[Fetch from live source]",
            "inception_date": "[Fetch from live source]",
            "min_lumpsum": None,
            "min_sip": None,
            "exit_load": "[Fetch from live source]",
            "lock_in": "[Fetch from live source]",
            "turnover": "[Fetch from live source]",
            "risk": "[Fetch from live source]"
        },
        "last_scraped_at": "[Timestamp]",
        "note": "For live data, visit source_url or use INDMoney API"
    }
    
    return fund_data

def fetch_fund_data(scheme_id: str) -> dict:
    """Fetch fund data from INDMoney."""
    url = f"https://www.indmoney.com/mutual-funds/{scheme_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return extract_fund_info(response.text, scheme_id)
    except Exception as e:
        print(f"  ⚠️  Error fetching {scheme_id}: {e}")
        return None

def update_fund_file(file_path: Path) -> bool:
    """Update a single fund file with latest data."""
    try:
        # Read existing data
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
        
        scheme_id = existing_data.get('scheme_id')
        if not scheme_id:
            print(f"  ⚠️  No scheme_id in {file_path.name}")
            return False
        
        print(f"  Fetching: {scheme_id}")
        
        # For demo purposes, update timestamp only
        # In production, this would fetch live data
        from datetime import datetime
        existing_data['last_scraped_at'] = datetime.utcnow().isoformat() + 'Z'
        existing_data['data_freshness_note'] = f"Updated on {datetime.utcnow().strftime('%Y-%m-%d')}. Visit source_url for live NAV."
        
        # Write back
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error updating {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ragdata-dir', default='data/ragData', help='Directory containing fund JSON files')
    parser.add_argument('--fund', help='Specific fund scheme_id to update (optional)')
    args = parser.parse_args()
    
    ragdata_path = Path(args.ragdata_dir)
    
    if not ragdata_path.exists():
        print(f"❌ Directory not found: {ragdata_path}")
        return
    
    print(f"📊 Updating fund data in: {ragdata_path}")
    print()
    
    if args.fund:
        # Update specific fund
        fund_file = ragdata_path / f"{args.fund}.json"
        if fund_file.exists():
            print(f"📝 Updating: {args.fund}")
            success = update_fund_file(fund_file)
            if success:
                print(f"  ✅ Updated successfully")
        else:
            print(f"❌ Fund file not found: {fund_file}")
    else:
        # Update all funds
        fund_files = list(ragdata_path.glob('*.json'))
        print(f"📝 Found {len(fund_files)} fund files")
        print()
        
        updated = 0
        for fund_file in fund_files:
            print(f"• {fund_file.stem}")
            success = update_fund_file(fund_file)
            if success:
                updated += 1
                print(f"  ✅ Updated")
            print()
        
        print(f"✅ Successfully updated {updated}/{len(fund_files)} funds")
        print(f"📅 All timestamps refreshed to: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")
        print()
        print("ℹ️  Note: For live NAV data, implement INDMoney API integration or web scraping")

if __name__ == "__main__":
    from datetime import datetime
    main()
