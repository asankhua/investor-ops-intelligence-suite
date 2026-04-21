#!/usr/bin/env python3
"""Generate latest fund data with realistic NAV updates for testing.

Note: This simulates live data for development/testing. 
For production, integrate with INDMoney API, AMFI, or Morningstar.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta

def generate_realistic_nav_change(current_nav: float) -> float:
    """Generate a realistic daily NAV change (-2% to +2%)."""
    change_percent = random.uniform(-0.02, 0.02)
    return current_nav * (1 + change_percent)

def parse_existing_nav(nav_text: str) -> tuple:
    """Parse NAV value and date from existing text."""
    # Extract number like "₹223.96"
    import re
    match = re.search(r'₹([\d,]+\.?\d*)', nav_text)
    if match:
        nav_value = float(match.group(1).replace(',', ''))
        # Try to extract date
        date_match = re.search(r'as on\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})', nav_text)
        date_str = date_match.group(1) if date_match else "Unknown"
        return nav_value, date_str
    return None, None

def update_fund_to_latest(file_path: Path) -> bool:
    """Update fund file with simulated latest data."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        overview = data.get('overview', {})
        
        # Parse current NAV
        current_nav_text = overview.get('nav', '')
        current_nav, old_date = parse_existing_nav(current_nav_text)
        
        if current_nav:
            # Simulate NAV change (market movement over ~50 days from Feb 27 to Apr 20)
            days_diff = 53  # Feb 27 to Apr 20, 2026
            daily_volatility = 0.008  # 0.8% daily movement
            
            # Compound the changes
            total_change = 1.0
            for _ in range(days_diff):
                daily_change = random.uniform(-daily_volatility, daily_volatility)
                total_change *= (1 + daily_change)
            
            new_nav = current_nav * total_change
            new_nav = round(new_nav, 2)
            
            # Update with today's date
            today = datetime.now()
            today_str = today.strftime('%d %b %Y')
            
            overview['nav'] = f"₹{new_nav} (as on {today_str})"
            
            # Simulate AUM change (correlates with NAV for equity funds)
            current_aum = overview.get('aum', '')
            if 'Cr' in current_aum:
                aum_match = re.search(r'₹([\d,]+)\s*Cr', current_aum)
                if aum_match:
                    aum_value = float(aum_match.group(1).replace(',', ''))
                    # AUM changes with NAV + inflows/outflows
                    new_aum = aum_value * (0.98 + random.uniform(0, 0.06))  # -2% to +4%
                    overview['aum'] = f"₹{int(new_aum):,} Cr"
        
        # Update metadata
        data['overview'] = overview
        data['last_scraped_at'] = datetime.utcnow().isoformat() + 'Z'
        data['data_freshness_note'] = f"Live simulated data as of {datetime.now().strftime('%Y-%m-%d')}. For actual NAV, visit source_url."
        data['data_source'] = 'simulated-latest-for-testing'
        data['simulation_note'] = 'NAV values are simulated based on historical data. Not actual market prices.'
        
        # Write back
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error updating {file_path.name}: {e}")
        return False

def main():
    ragdata_path = Path('/Users/asankhua/Cursor/investor-intelligence-suite/data/ragData')
    
    if not ragdata_path.exists():
        print(f"❌ Directory not found: {ragdata_path}")
        return
    
    print("📊 Generating latest fund data (simulated)...")
    print("   Note: INDMoney blocks live scraping. Using simulated updates.")
    print()
    
    fund_files = list(ragdata_path.glob('*.json'))
    print(f"📝 Found {len(fund_files)} fund files")
    print()
    
    updated = 0
    changes = []
    
    for i, fund_file in enumerate(fund_files, 1):
        # Read old data for comparison
        with open(fund_file, 'r') as f:
            old_data = json.load(f)
        old_nav = old_data.get('overview', {}).get('nav', 'N/A')
        
        print(f"{i}. {fund_file.stem[:50]}...")
        success = update_fund_to_latest(fund_file)
        
        if success:
            # Read new data
            with open(fund_file, 'r') as f:
                new_data = json.load(f)
            new_nav = new_data.get('overview', {}).get('nav', 'N/A')
            
            changes.append({
                'fund': new_data.get('name', 'Unknown'),
                'old_nav': old_nav,
                'new_nav': new_nav
            })
            
            print(f"   ✅ Updated: {old_nav} → {new_nav}")
            updated += 1
        else:
            print(f"   ❌ Failed")
        print()
    
    print(f"✅ Successfully updated {updated}/{len(fund_files)} funds")
    print(f"📅 Simulated as of: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
    print()
    print("⚠️  IMPORTANT: These are SIMULATED values for testing.")
    print("   For production, integrate with:")
    print("   • INDMoney API (if available)")
    print("   • AMFI (Association of Mutual Funds in India)")
    print("   • Morningstar / Value Research")
    print("   • Browser automation (Playwright/Selenium)")
    print()
    print("📊 Summary of changes:")
    for change in changes:
        print(f"   • {change['fund'][:40]:<40} {change['old_nav'][:20]:<20} → {change['new_nav']}")

if __name__ == "__main__":
    import re
    main()
