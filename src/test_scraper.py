#!/usr/bin/env python3
"""
Simple test script to debug the scraper and examine HTML structure
"""

import requests
from bs4 import BeautifulSoup
import time
import random

def test_confs_tech_structure():
    """Test the structure of confs.tech/cfp to debug scraping issues"""
    
    url = "https://confs.tech/cfp"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"Testing access to: {url}")
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content Length: {len(response.text)} characters")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for basic HTML structure
        title = soup.find('title')
        print(f"Page Title: {title.get_text() if title else 'No title found'}")
        
        # Look for potential conference containers
        print("\n=== Looking for common conference selectors ===")
        
        # Common patterns for conference/event listings
        selectors_to_test = [
            '.conference', '.event', '.cfp', '.listing',
            '.conference-item', '.event-item', '.cfp-item',
            '.card', '.conference-card', '.event-card',
            'article', '.post', '.item',
            '[data-testid*="conference"]', '[data-testid*="event"]',
            '.list-item', '.grid-item'
        ]
        
        for selector in selectors_to_test:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector '{selector}'")
                # Show first element for inspection
                if len(elements) > 0:
                    first_elem = elements[0]
                    print(f"  First element preview: {str(first_elem)[:200]}...")
        
        # Look for any divs with specific classes
        print("\n=== All div classes found ===")
        all_divs = soup.find_all('div', class_=True)
        unique_classes = set()
        for div in all_divs:
            classes = div.get('class', [])
            for cls in classes:
                unique_classes.add(cls)
        
        sorted_classes = sorted(unique_classes)
        print(f"Found {len(sorted_classes)} unique div classes:")
        for cls in sorted_classes[:20]:  # Show first 20
            print(f"  .{cls}")
        if len(sorted_classes) > 20:
            print(f"  ... and {len(sorted_classes) - 20} more")
        
        # Look for any text containing "CFP" or conference-related keywords
        print("\n=== Looking for CFP-related text ===")
        cfp_keywords = ['cfp', 'call for papers', 'deadline', 'submit', 'proposal', 'conference']
        page_text = soup.get_text().lower()
        
        for keyword in cfp_keywords:
            if keyword in page_text:
                print(f"Found keyword '{keyword}' in page text")
        
        # Check if page uses JavaScript heavily
        script_tags = soup.find_all('script')
        print(f"\n=== JavaScript Analysis ===")
        print(f"Found {len(script_tags)} script tags")
        
        # Look for frameworks
        frameworks = ['react', 'vue', 'angular', 'ember', 'svelte']
        for framework in frameworks:
            if framework in page_text:
                print(f"Possible {framework.title()} usage detected")
        
        # Save HTML for manual inspection
        with open('logs/confs_tech_cfp_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nHTML saved to logs/confs_tech_cfp_debug.html for manual inspection")
        
        return True
        
    except Exception as e:
        print(f"Error testing website: {e}")
        return False

if __name__ == "__main__":
    test_confs_tech_structure() 