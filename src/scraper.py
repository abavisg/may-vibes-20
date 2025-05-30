#!/usr/bin/env python3
"""
Event Scraper Agent for CFP Scout
Scrapes tech events with open CFPs from https://confs.tech/cfp
Uses Selenium for JavaScript-rendered content
"""

import json
import logging
import re
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CFPScraper:
    """Scraper for CFP events from confs.tech using Selenium"""
    
    def __init__(self, headless: bool = True):
        self.base_url = "https://confs.tech"
        self.cfp_url = "https://confs.tech/cfp"
        self.headless = headless
        self.driver = None
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Install and setup ChromeDriver automatically
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"ChromeDriverManager failed: {e}, trying system Chrome")
                # Fallback to system Chrome if available
                self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info("Chrome WebDriver setup successful")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            return False
    
    def _cleanup_driver(self):
        """Cleanup WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver cleanup completed")
            except Exception as e:
                logger.warning(f"Error during WebDriver cleanup: {e}")
    
    def get_events(self) -> List[Dict]:
        """
        Main function to scrape CFP events from confs.tech/cfp
        
        Returns:
            List[Dict]: List of event dictionaries with keys:
                - title: Event name
                - cfp_deadline: CFP submission deadline  
                - location: Event location
                - tags: List of event tags/topics
                - link: Event website URL
                - description: Event description (if available)
                - scraped_at: When the data was scraped
        """
        if not self._setup_driver():
            return []
        
        try:
            logger.info("Starting CFP events scraping from confs.tech/cfp")
            
            # Add random delay to be polite
            time.sleep(random.uniform(2, 4))
            
            # Navigate to the CFP page
            self.driver.get(self.cfp_url)
            
            # Wait for the page to load and content to be rendered
            logger.info("Waiting for page content to load...")
            
            # Wait for React to render content - look for conference items
            wait = WebDriverWait(self.driver, 15)
            
            try:
                # Wait for conference items to appear
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ConferenceItem_ConferenceItem__orfQz")))
                logger.info("Conference items detected")
            except TimeoutException:
                logger.warning("Timeout waiting for conference items, proceeding anyway")
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page source after JavaScript execution
            html_content = self.driver.page_source
            
            # Save rendered HTML for debugging
            with open('logs/confs_tech_cfp_rendered.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("Rendered HTML saved for debugging")
            
            events = self._parse_events_selenium()
            
            logger.info(f"Successfully scraped {len(events)} CFP events")
            return events
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []
        finally:
            self._cleanup_driver()
    
    def _parse_events_selenium(self) -> List[Dict]:
        """Parse events using Selenium WebDriver based on actual confs.tech structure"""
        events = []
        
        try:
            # Find all conference item elements
            conference_elements = self.driver.find_elements(By.CLASS_NAME, "ConferenceItem_ConferenceItem__orfQz")
            logger.info(f"Found {len(conference_elements)} conference items")
            
            for i, element in enumerate(conference_elements):
                try:
                    event_data = self._extract_event_data_from_conference_item(element)
                    if event_data and event_data.get('title'):
                        events.append(event_data)
                        logger.debug(f"Extracted event {i+1}: {event_data['title']}")
                except Exception as e:
                    logger.warning(f"Error parsing conference item {i+1}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in parse_events_selenium: {e}")
        
        return events
    
    def _extract_event_data_from_conference_item(self, element) -> Optional[Dict]:
        """Extract event data from a conference item element"""
        event = {
            'title': '',
            'cfp_deadline': '',
            'location': '',
            'tags': [],
            'link': '',
            'description': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Extract title and link from the conference name heading
            try:
                title_element = element.find_element(By.CSS_SELECTOR, ".Heading_Heading-4__SF2ex .Link_Link__BisAg")
                event['title'] = title_element.text.strip()
                event['link'] = title_element.get_attribute('href') or ''
            except Exception as e:
                logger.debug(f"Could not extract title/link: {e}")
                return None
            
            # Extract location and date from the location paragraph
            try:
                location_element = element.find_element(By.CLASS_NAME, "ConferenceItem_p__r7Z+7")
                location_text = location_element.text.strip()
                
                # Split by the bullet point to separate location from date
                if '・' in location_text:
                    location_part = location_text.split('・')[0].strip()
                    event['location'] = location_part
                else:
                    event['location'] = location_text
                    
                # Handle online events specifically
                if not event['location'] or event['location'].lower() in ['online', '']:
                    event['location'] = 'Online'
                    
            except Exception as e:
                logger.debug(f"Could not extract location: {e}")
            
            # Extract CFP deadline - try multiple approaches
            try:
                # First try to find CFP links with deadline text
                cfp_links = element.find_elements(By.CSS_SELECTOR, "a[href*='cfp'], a[href*='sessionize'], a[href*='forms'], a[href*='typeform']")
                for cfp_link in cfp_links:
                    link_text = cfp_link.text.strip()
                    if 'CFP closes' in link_text or 'closes' in link_text:
                        # Extract the date part after "CFP closes"
                        if 'CFP closes' in link_text:
                            deadline = link_text.replace('CFP closes', '').strip()
                        else:
                            deadline = link_text.replace('closes', '').strip()
                        event['cfp_deadline'] = deadline
                        break
                
                # If no deadline found in CFP links, try to find any text with "CFP closes"
                if not event['cfp_deadline']:
                    element_text = element.text
                    cfp_pattern = r'CFP closes\s+([A-Za-z]+\s+\d{1,2})'
                    match = re.search(cfp_pattern, element_text, re.IGNORECASE)
                    if match:
                        event['cfp_deadline'] = match.group(1)
                        
            except Exception as e:
                logger.debug(f"Could not extract CFP deadline: {e}")
            
            # Extract tags/topics
            try:
                topic_elements = element.find_elements(By.CLASS_NAME, "ConferenceItem_topic__Xjqb5")
                for topic_elem in topic_elements:
                    topic_text = topic_elem.text.strip()
                    if topic_text.startswith('#'):
                        topic_text = topic_text[1:]  # Remove the # symbol
                    if topic_text:
                        event['tags'].append(topic_text)
            except Exception as e:
                logger.debug(f"Could not extract topics: {e}")
            
            # Extract additional description from JSON-LD if available
            try:
                json_script = element.find_element(By.CSS_SELECTOR, "script[type='application/ld+json']")
                if json_script:
                    json_text = json_script.get_attribute('innerHTML')
                    json_data = json.loads(json_text)
                    
                    # Add additional info from structured data
                    if 'description' in json_data:
                        event['description'] = json_data['description']
                    
                    # Enhance location with structured data if current location is empty or just "Online"
                    if 'location' in json_data and isinstance(json_data['location'], dict):
                        location_data = json_data['location']
                        if 'address' in location_data and isinstance(location_data['address'], dict):
                            address = location_data['address']
                            city = address.get('addressLocality', '')
                            country = address.get('addressCountry', '')
                            if city and country and city != 'null' and country != 'null':
                                structured_location = f"{city}, {country}"
                                # Only use structured location if we don't have a good location already
                                if not event['location'] or event['location'] == 'Online':
                                    event['location'] = structured_location
                                elif event['location'] and structured_location not in event['location']:
                                    # If we have a partial location, try to enhance it
                                    if len(event['location']) < len(structured_location):
                                        event['location'] = structured_location
                            else:
                                # If structured data shows null/null, it's likely an online event
                                if not event['location'] and (city == 'null' or country == 'null'):
                                    event['location'] = 'Online'
                             
            except Exception as e:
                logger.debug(f"Could not extract JSON-LD data: {e}")
            
            # Final check for empty location - default to Online
            if not event['location']:
                event['location'] = 'Online'
            
        except Exception as e:
            logger.debug(f"Error extracting data from conference item: {e}")
        
        # Only return event if we have at least a title
        return event if event['title'] else None
    
    def save_events_to_json(self, events: List[Dict], filename: str = 'cfp_events.json') -> None:
        """Save events to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(events)} events to {filename}")
        except Exception as e:
            logger.error(f"Error saving events to JSON: {e}")

def get_events() -> List[Dict]:
    """
    Main function to get CFP events - this is the interface other modules will use
    
    Returns:
        List[Dict]: List of scraped CFP events
    """
    scraper = CFPScraper(headless=True)
    return scraper.get_events()

if __name__ == "__main__":
    # Test the scraper
    events = get_events()
    
    if events:
        # Print first few events for verification
        print(f"\nFound {len(events)} CFP events:")
        print("="*50)
        
        for i, event in enumerate(events[:5]):  # Show first 5 events
            print(f"\nEvent {i+1}:")
            print(f"Title: {event['title']}")
            print(f"CFP Deadline: {event['cfp_deadline']}")
            print(f"Location: {event['location']}")
            print(f"Tags: {', '.join(event['tags']) if event['tags'] else 'None'}")
            print(f"Link: {event['link']}")
            print(f"Description: {event['description'][:100]}..." if event['description'] else "No description")
        
        # Save to JSON for testing
        scraper = CFPScraper()
        scraper.save_events_to_json(events, 'logs/cfp_events_test.json')
    else:
        print("No events found. The website structure might have changed.") 