#!/usr/bin/env python3
"""Update ragData fund files from chunks.json (latest available data)."""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_nav(text: str) -> tuple:
    """Extract NAV value and date from chunk text."""
    # Pattern: "As on 27 Feb 2026, the NAV of HDFC Mid Cap Fund is ₹223.96"
    match = re.search(r'As on\s+([\d]{1,2}\s+[A-Za-z]+\s+\d{4}),?\s+.*?NAV.*?is\s+₹?([\d,]+\.?\d*)', text)
    if match:
        return match.group(2).replace(',', ''), match.group(1)
    
    # Alternative: "NAV is ₹223.96 (as on 27 Feb 2026)"
    match = re.search(r'NAV.*?is\s+₹?([\d,]+\.?\d*).*?as on\s+([\d]{1,2}\s+[A-Za-z]+\s+\d{4})', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(',', ''), match.group(2)
    
    return None, None

def extract_aum(text: str) -> str:
    """Extract AUM from chunk text."""
    match = re.search(r'AUM.*?are\s+₹?([\d,]+)\s*Cr', text)
    if match:
        return '₹' + match.group(1).replace(',', '') + ' Cr'
    return None

def extract_expense_ratio(text: str) -> str:
    """Extract expense ratio from chunk text."""
    match = re.search(r'expense ratio.*?is\s+(\d+\.?\d*)\s*%', text, re.IGNORECASE)
    if match:
        return match.group(1) + '%'
    return None

def extract_exit_load(text: str) -> str:
    """Extract exit load from chunk text."""
    match = re.search(r'[Ee]xit [Ll]oad.*?is\s+(\d+\.?\d*)\s*%', text)
    if match:
        return match.group(1) + '%'
    return None

def extract_benchmark(text: str) -> str:
    """Extract benchmark from chunk text."""
    match = re.search(r'benchmark is\s+([A-Za-z\s\d]+?)(?:\.|\n)', text)
    if match:
        return match.group(1).strip()
    return None

def extract_min_investment(text: str) -> tuple:
    """Extract minimum investment (lumpsum, sip) from chunk text."""
    lumpsum = None
    sip = None
    
    # Look for lumpsum
    match = re.search(r'[Ll]umpsum[:\-]?\s*₹?([\d,]+)', text)
    if match:
        lumpsum = '₹' + match.group(1).replace(',', '')
    
    # Look for SIP
    match = re.search(r'SIP[:\-]?\s*₹?([\d,]+)', text)
    if match:
        sip = '₹' + match.group(1).replace(',', '')
    
    return lumpsum, sip

def extract_lock_in(text: str) -> str:
    """Extract lock-in period from chunk text."""
    match = re.search(r'[Ll]ock-in [Pp]eriod[:\-]?\s*(No [Ll]ock-in|\d+\s*\w+)', text)
    if match:
        return match.group(1)
    return None

def extract_turnover(text: str) -> str:
    """Extract turnover from chunk text."""
    match = re.search(r'[Tt]urnover[:\-]?\s*(\d+\.?\d*)\s*%', text)
    if match:
        return match.group(1) + '%'
    return None

def extract_risk(text: str) -> str:
    """Extract risk profile from chunk text."""
    match = re.search(r'(?:SEBI )?[Rr]isk [Ll]abel?[:\-]?\s*([A-Za-z\s]+[Rr]isk)', text)
    if match:
        return match.group(1).strip()
    return None

def extract_returns(text: str) -> dict:
    """Extract returns data from chunk text."""
    returns = {}
    
    # Since inception
    match = re.search(r'[Ss]ince [Ii]nception[:\-]?\s*(\d+\.?\d*)%?\s*/?\s*per year', text)
    if match:
        returns['since_inception'] = match.group(1) + '%/per year Since Inception'
    
    # Other returns might be in separate chunks or tables
    return returns

def load_chunks(chunks_path: Path) -> list:
    """Load chunks from JSON file."""
    with open(chunks_path, 'r') as f:
        return json.load(f)

def get_latest_fund_data(chunks: list, scheme_id: str) -> dict:
    """Extract all available data for a fund from chunks."""
    fund_chunks = [c for c in chunks if c.get('scheme_id') == scheme_id]
    
    if not fund_chunks:
        return None
    
    data = {
        'nav': None,
        'nav_date': None,
        'aum': None,
        'expense_ratio': None,
        'exit_load': None,
        'benchmark': None,
        'min_lumpsum': None,
        'min_sip': None,
        'lock_in': None,
        'turnover': None,
        'risk': None,
        'returns_since_inception': None,
        'scraped_at': None
    }
    
    # Get latest scraped_at
    dates = [c.get('scraped_at', '') for c in fund_chunks if c.get('scraped_at')]
    if dates:
        data['scraped_at'] = max(dates)
    
    # Extract data from all chunks for this fund
    for chunk in fund_chunks:
        text = chunk.get('text', '')
        chunk_type = chunk.get('chunk_type', '')
        
        # NAV (usually in overview chunk)
        if chunk_type == 'overview' or not data['nav']:
            nav, nav_date = extract_nav(text)
            if nav:
                data['nav'] = nav
                data['nav_date'] = nav_date
            if not data['aum']:
                data['aum'] = extract_aum(text)
            if not data['benchmark']:
                data['benchmark'] = extract_benchmark(text)
        
        # Fees (usually in fees chunk)
        if chunk_type in ['fees', 'expenses'] or not data['expense_ratio']:
            if not data['expense_ratio']:
                data['expense_ratio'] = extract_expense_ratio(text)
            if not data['exit_load']:
                data['exit_load'] = extract_exit_load(text)
        
        # Min investment (usually in min_investment chunk)
        if chunk_type == 'min_investment':
            lumpsum, sip = extract_min_investment(text)
            if not data['min_lumpsum']:
                data['min_lumpsum'] = lumpsum
            if not data['min_sip']:
                data['min_sip'] = sip
            if not data['lock_in']:
                data['lock_in'] = extract_lock_in(text)
        
        # Risk (usually in risk chunk)
        if chunk_type == 'risk' or not data['risk']:
            if not data['risk']:
                data['risk'] = extract_risk(text)
            if not data['turnover']:
                data['turnover'] = extract_turnover(text)
            if not data['benchmark']:
                data['benchmark'] = extract_benchmark(text)
        
        # Returns (usually in returns chunk)
        if chunk_type == 'returns':
            returns = extract_returns(text)
            if returns.get('since_inception'):
                data['returns_since_inception'] = returns['since_inception']
    
    return data

def update_fund_file(ragdata_path: Path, scheme_id: str, fund_data: dict):
    """Update a single fund file with latest data."""
    file_path = ragdata_path / f"{scheme_id}.json"
    
    if not file_path.exists():
        print(f"  ⚠️  File not found: {file_path.name}")
        return False
    
    # Load existing file
    with open(file_path, 'r') as f:
        existing = json.load(f)
    
    # Update with new data
    overview = existing.get('overview', {})
    
    if fund_data['nav'] and fund_data['nav_date']:
        overview['nav'] = f"₹{fund_data['nav']} (as on {fund_data['nav_date']})"
    
    if fund_data['expense_ratio']:
        overview['expense_ratio'] = fund_data['expense_ratio']
    
    if fund_data['exit_load']:
        overview['exit_load'] = fund_data['exit_load']
    
    if fund_data['aum']:
        overview['aum'] = fund_data['aum']
    
    if fund_data['benchmark']:
        overview['benchmark'] = fund_data['benchmark']
    
    if fund_data['min_lumpsum']:
        overview['min_lumpsum'] = fund_data['min_lumpsum']
    
    if fund_data['min_sip']:
        overview['min_sip'] = fund_data['min_sip']
    
    if fund_data['lock_in']:
        overview['lock_in'] = fund_data['lock_in']
    
    if fund_data['turnover']:
        overview['turnover'] = fund_data['turnover']
    
    if fund_data['risk']:
        overview['risk'] = fund_data['risk']
    
    if fund_data['returns_since_inception']:
        overview['returns_since_inception'] = fund_data['returns_since_inception']
    
    # Update metadata
    existing['overview'] = overview
    existing['last_scraped_at'] = fund_data.get('scraped_at') or datetime.utcnow().isoformat() + 'Z'
    existing['data_freshness_note'] = f"Updated from chunks.json on {datetime.utcnow().strftime('%Y-%m-%d')}. Data as of {fund_data.get('nav_date', 'latest available')}."
    existing['data_source'] = 'chunks.json (pre-scraped from INDMoney)'
    
    # Write back
    with open(file_path, 'w') as f:
        json.dump(existing, f, indent=2)
    
    return True

def main():
    # Paths
    base_path = Path('/Users/asankhua/Cursor/investor-intelligence-suite')
    chunks_path = Path('/Users/asankhua/Cursor/rag-based-mutualfund-faqchatbot/data/phase2/chunks.json')
    ragdata_path = base_path / 'data' / 'ragData'
    
    if not chunks_path.exists():
        print(f"❌ chunks.json not found: {chunks_path}")
        return
    
    if not ragdata_path.exists():
        print(f"❌ ragData directory not found: {ragdata_path}")
        return
    
    print(f"📊 Loading chunks from: {chunks_path}")
    chunks = load_chunks(chunks_path)
    print(f"   Loaded {len(chunks)} chunks")
    print()
    
    # Get list of fund files
    fund_files = list(ragdata_path.glob('*.json'))
    print(f"📝 Found {len(fund_files)} fund files to update")
    print()
    
    updated = 0
    for i, fund_file in enumerate(fund_files, 1):
        scheme_id = fund_file.stem
        print(f"{i}. {scheme_id[:60]}...")
        
        # Get latest data from chunks
        fund_data = get_latest_fund_data(chunks, scheme_id)
        
        if fund_data:
            success = update_fund_file(ragdata_path, scheme_id, fund_data)
            if success:
                print(f"   ✅ Updated with data from {fund_data.get('nav_date', 'chunks.json')}")
                if fund_data.get('nav'):
                    print(f"      NAV: ₹{fund_data['nav']}")
                if fund_data.get('expense_ratio'):
                    print(f"      Expense: {fund_data['expense_ratio']}")
                updated += 1
            else:
                print(f"   ❌ Failed to update")
        else:
            print(f"   ⚠️  No matching chunks found for this fund")
        print()
    
    print(f"✅ Successfully updated {updated}/{len(fund_files)} funds")
    print(f"📅 Data source: chunks.json (scraped from INDMoney)")
    print(f"🕐 Updated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC")

if __name__ == "__main__":
    main()
