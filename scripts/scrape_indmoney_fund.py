#!/usr/bin/env python3
"""Scrape live mutual fund data from INDMoney."""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run(["pip3", "install", "requests", "beautifulsoup4", "-q"])
    import requests
    from bs4 import BeautifulSoup

def parse_nav_value(nav_text: str) -> str:
    """Extract NAV value from text like '₹147.10 (as on 20 Apr 2025)'."""
    if not nav_text:
        return None
    # Extract the rupee value
    match = re.search(r'₹([\d,]+\.?\d*)', nav_text)
    if match:
        return match.group(1).replace(',', '')
    return None

def parse_percentage(text: str) -> str:
    """Extract percentage from text like '21.5%' or '0.67%'."""
    if not text:
        return None
    match = re.search(r'(\d+\.?\d*)\s*%', text)
    if match:
        return match.group(1) + '%'
    return text.strip() if text else None

def scrape_fund_data(scheme_id: str) -> dict:
    """Scrape fund data from INDMoney website."""
    url = f"https://www.indmoney.com/mutual-funds/{scheme_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        print(f"    Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract fund name from title or h1
        fund_name = scheme_id
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text()
            # Clean up title - remove "Mutual Fund" suffix
            fund_name = title_text.replace(' Mutual Fund', '').replace(' | INDmoney', '').strip()
        
        # Try to find NAV - look for common patterns
        nav = None
        nav_date = None
        
        # Look for NAV in the page
        nav_patterns = [
            r'₹[\d,]+\.?\d*.*as on.*\d{1,2}\s+[A-Za-z]+,?\s*\d{4}',
            r'NAV.*₹[\d,]+\.?\d*',
            r'Net Asset Value.*₹[\d,]+\.?\d*'
        ]
        
        page_text = soup.get_text()
        for pattern in nav_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                nav_text = match.group(0)
                nav = parse_nav_value(nav_text)
                # Extract date
                date_match = re.search(r'as on\s+(\d{1,2}\s+[A-Za-z]+,?\s*\d{4})', nav_text)
                if date_match:
                    nav_date = date_match.group(1)
                break
        
        # Look for expense ratio
        expense_ratio = None
        expense_patterns = [
            r'Expense Ratio\s*[:\-]?\s*(\d+\.?\d*)\s*%',
            r'Expense\s*[:\-]?\s*(\d+\.?\d*)\s*%',
        ]
        for pattern in expense_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                expense_ratio = match.group(1) + '%'
                break
        
        # Look for exit load
        exit_load = None
        exit_patterns = [
            r'Exit Load\s*[:\-]?\s*(\d+\.?\d*)\s*%',
            r'Exit\s*Load\s*[:\-]?\s*(No\s*Lock-in|Nil|[\d\.]+\s*%)',
        ]
        for pattern in exit_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                exit_load_text = match.group(1)
                if 'no lock' in exit_load_text.lower():
                    exit_load = "0%"
                else:
                    exit_load = exit_load_text if '%' in exit_load_text else exit_load_text + '%'
                break
        
        # Look for AUM
        aum = None
        aum_patterns = [
            r'AUM\s*[:\-]?\s*₹?([\d,]+\.?\d*)\s*(Cr|Lakhs?|L)',
            r'Assets\s*Under\s*Management\s*[:\-]?\s*₹?([\d,]+\.?\d*)\s*(Cr|Lakhs?|L)',
        ]
        for pattern in aum_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                aum = '₹' + match.group(1) + ' ' + match.group(2)
                break
        
        # Look for returns
        returns_1y = None
        returns_3y = None
        returns_5y = None
        
        # Look for return patterns
        return_patterns = [
            (r'1\s*Year.*?(\d+\.?\d*)\s*%', '1y'),
            (r'3\s*Year.*?(\d+\.?\d*)\s*%', '3y'),
            (r'5\s*Year.*?(\d+\.?\d*)\s*%', '5y'),
        ]
        
        for pattern, period in return_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                if period == '1y':
                    returns_1y = matches[0] + '%'
                elif period == '3y':
                    returns_3y = matches[0] + '%'
                elif period == '5y':
                    returns_5y = matches[0] + '%'
        
        # Look for benchmark
        benchmark = None
        benchmark_patterns = [
            r'Benchmark\s*[:\-]?\s*([A-Za-z\s\d]+?)(?:\n|$)',
            r'Benchmark\s*Index\s*[:\-]?\s*([A-Za-z\s\d]+?)(?:\n|$)',
        ]
        for pattern in benchmark_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                benchmark = match.group(1).strip()
                break
        
        return {
            "scheme_id": scheme_id,
            "name": fund_name,
            "source_url": url,
            "overview": {
                "nav": f"₹{nav} (as on {nav_date})" if nav and nav_date else (f"₹{nav}" if nav else "[Check source_url]"),
                "expense_ratio": expense_ratio or "[Check source_url]",
                "exit_load": exit_load or "[Check source_url]",
                "aum": aum or "[Check source_url]",
                "returns_1y": returns_1y or "[Check source_url]",
                "returns_3y": returns_3y or "[Check source_url]",
                "returns_5y": returns_5y or "[Check source_url]",
                "benchmark": benchmark or "[Check source_url]",
                "returns_since_inception": "[Check source_url]",
                "inception_date": "[Check source_url]",
                "min_lumpsum": "[Check source_url]",
                "min_sip": "[Check source_url]",
                "lock_in": "[Check source_url]",
                "turnover": "[Check source_url]",
                "risk": "[Check source_url]"
            },
            "last_scraped_at": datetime.utcnow().isoformat() + 'Z',
            "data_freshness_note": f"Live scrape on {datetime.utcnow().strftime('%Y-%m-%d')}. Visit source_url for complete data."
        }
        
    except Exception as e:
        print(f"    ⚠️  Error scraping {scheme_id}: {e}")
        return None

def update_fund_file(file_path: Path) -> bool:
    """Update a single fund file with scraped data."""
    try:
        # Read existing data to get scheme_id
        with open(file_path, 'r') as f:
            existing_data = json.load(f)
        
        scheme_id = existing_data.get('scheme_id')
        if not scheme_id:
            print(f"  ⚠️  No scheme_id in {file_path.name}")
            return False
        
        # Scrape new data
        new_data = scrape_fund_data(scheme_id)
        if not new_data:
            return False
        
        # Preserve any existing data that wasn't found in scrape
        for key in ['returns_since_inception', 'inception_date', 'min_lumpsum', 'min_sip', 'lock_in', 'turnover', 'risk']:
            if existing_data.get('overview', {}).get(key) and new_data['overview'].get(key) == '[Check source_url]':
                new_data['overview'][key] = existing_data['overview'][key]
        
        # Write back
        with open(file_path, 'w') as f:
            json.dump(new_data, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error updating {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ragdata-dir', default='data/ragData', help='Directory containing fund JSON files')
    args = parser.parse_args()
    
    ragdata_path = Path(args.ragdata_dir)
    
    if not ragdata_path.exists():
        print(f"❌ Directory not found: {ragdata_path}")
        return
    
    print(f"📊 Scraping live fund data from INDMoney...")
    print(f"   Directory: {ragdata_path}")
    print()
    
    # Update all funds
    fund_files = list(ragdata_path.glob('*.json'))
    print(f"📝 Found {len(fund_files)} fund files")
    print()
    
    updated = 0
    for i, fund_file in enumerate(fund_files, 1):
        print(f"{i}. {fund_file.stem[:50]}...")
        success = update_fund_file(fund_file)
        if success:
            updated += 1
            print(f"   ✅ Updated with live data")
        else:
            print(f"   ❌ Failed to update")
        print()
    
    print(f"✅ Successfully updated {updated}/{len(fund_files)} funds")
    print(f"📅 Scraped at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")

if __name__ == "__main__":
    main()
