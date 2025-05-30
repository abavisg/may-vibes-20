#!/usr/bin/env python3
"""
Event MCP (Message Control Protocol) Agent for CFP Scout
Central orchestrator that coordinates data flow between scrapers, filters, and email sender
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NormalizedEvent:
    """Normalized event data structure"""
    id: str  # Unique identifier (hash of title + link)
    title: str
    cfp_deadline: str
    location: str
    tags: List[str]
    link: str
    description: str
    source: str  # Which scraper provided this event
    scraped_at: str
    normalized_at: str
    relevance_score: Optional[float] = None
    is_filtered: bool = False

class EventMCP:
    """
    Event Message Control Protocol Agent
    Central orchestrator for CFP Scout system
    """
    
    def __init__(self, storage_dir: str = "logs"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Storage files
        self.raw_events_file = self.storage_dir / "raw_events.json"
        self.normalized_events_file = self.storage_dir / "normalized_events.json"
        self.filtered_events_file = self.storage_dir / "filtered_events.json"
        
        logger.info(f"Event MCP initialized with storage dir: {self.storage_dir}")
    
    def process_pipeline(self, scraper_modules: List[str] = None) -> Dict:
        """
        Main pipeline execution method
        
        Args:
            scraper_modules: List of scraper module names to run (defaults to ['scraper'])
        
        Returns:
            Dict with pipeline results and statistics
        """
        if scraper_modules is None:
            scraper_modules = ['scraper']
        
        pipeline_start = datetime.now()
        results = {
            'pipeline_start': pipeline_start.isoformat(),
            'scrapers_run': [],
            'raw_events_count': 0,
            'normalized_events_count': 0,
            'filtered_events_count': 0,
            'emails_sent': 0,
            'errors': [],
            'pipeline_duration': None
        }
        
        try:
            logger.info("Starting Event MCP pipeline execution")
            
            # Step 1: Collect raw events from scrapers
            raw_events = self._collect_raw_events(scraper_modules)
            results['raw_events_count'] = len(raw_events)
            results['scrapers_run'] = scraper_modules
            
            if not raw_events:
                logger.warning("No raw events collected from scrapers")
                return results
            
            # Step 2: Normalize and store events
            normalized_events = self._normalize_events(raw_events)
            results['normalized_events_count'] = len(normalized_events)
            
            # Step 3: Filter events using LLM
            filtered_events = self._filter_events(normalized_events)
            results['filtered_events_count'] = len(filtered_events)
            
            # Step 4: Send emails if we have relevant events
            if filtered_events:
                email_success = self._send_emails(filtered_events)
                results['emails_sent'] = 1 if email_success else 0
            else:
                logger.info("No filtered events to send via email")
            
            # Calculate duration
            pipeline_end = datetime.now()
            results['pipeline_duration'] = str(pipeline_end - pipeline_start)
            
            logger.info(f"Pipeline completed successfully in {results['pipeline_duration']}")
            logger.info(f"Summary: {results['raw_events_count']} raw → {results['normalized_events_count']} normalized → {results['filtered_events_count']} filtered")
            
        except Exception as e:
            error_msg = f"Pipeline execution failed: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def _collect_raw_events(self, scraper_modules: List[str]) -> List[Dict]:
        """Collect raw events from specified scraper modules"""
        all_raw_events = []
        
        for module_name in scraper_modules:
            try:
                logger.info(f"Running scraper: {module_name}")
                
                # Dynamically import and run the scraper
                if module_name == 'scraper':
                    # Try relative import first, then absolute
                    try:
                        from . import scraper
                        events = scraper.get_events()
                    except ImportError:
                        # Fallback to absolute import for standalone execution
                        import sys
                        import os
                        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                        import scraper
                        events = scraper.get_events()
                else:
                    # For future scrapers, use dynamic import
                    try:
                        module = __import__(f'src.{module_name}', fromlist=[module_name])
                        events = module.get_events()
                    except ImportError:
                        # Fallback for standalone execution
                        import sys
                        import os
                        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                        module = __import__(module_name)
                        events = module.get_events()
                
                # Add source information
                for event in events:
                    event['source'] = module_name
                
                all_raw_events.extend(events)
                logger.info(f"Scraper {module_name} collected {len(events)} events")
                
            except Exception as e:
                error_msg = f"Failed to run scraper {module_name}: {e}"
                logger.error(error_msg)
                continue
        
        # Save raw events
        self._save_events(all_raw_events, self.raw_events_file)
        logger.info(f"Total raw events collected: {len(all_raw_events)}")
        
        return all_raw_events
    
    def _normalize_events(self, raw_events: List[Dict]) -> List[NormalizedEvent]:
        """Normalize raw events into consistent data structure"""
        normalized_events = []
        seen_ids = set()
        
        for raw_event in raw_events:
            try:
                # Create unique ID based on title and link
                event_id = self._generate_event_id(raw_event.get('title', ''), raw_event.get('link', ''))
                
                # Skip duplicates
                if event_id in seen_ids:
                    logger.debug(f"Skipping duplicate event: {raw_event.get('title', 'Unknown')}")
                    continue
                seen_ids.add(event_id)
                
                # Create normalized event
                normalized_event = NormalizedEvent(
                    id=event_id,
                    title=self._clean_text(raw_event.get('title', '')),
                    cfp_deadline=self._normalize_deadline(raw_event.get('cfp_deadline', '')),
                    location=self._clean_text(raw_event.get('location', 'Online')),
                    tags=self._normalize_tags(raw_event.get('tags', [])),
                    link=raw_event.get('link', ''),
                    description=self._clean_text(raw_event.get('description', '')),
                    source=raw_event.get('source', 'unknown'),
                    scraped_at=raw_event.get('scraped_at', ''),
                    normalized_at=datetime.now().isoformat()
                )
                
                # Validate required fields
                if not normalized_event.title or not normalized_event.link:
                    logger.warning(f"Skipping event with missing required fields: {raw_event}")
                    continue
                
                normalized_events.append(normalized_event)
                
            except Exception as e:
                logger.warning(f"Failed to normalize event {raw_event}: {e}")
                continue
        
        # Save normalized events
        normalized_dicts = [asdict(event) for event in normalized_events]
        self._save_events(normalized_dicts, self.normalized_events_file)
        
        logger.info(f"Normalized {len(normalized_events)} events (removed {len(raw_events) - len(normalized_events)} duplicates/invalid)")
        
        return normalized_events
    
    def _filter_events(self, normalized_events: List[NormalizedEvent]) -> List[NormalizedEvent]:
        """Filter events using LLM-based relevance scoring"""
        try:
            logger.info("Starting LLM-based event filtering")
            
            # Prepare events for filtering (convert to dict format)
            events_for_filtering = [asdict(event) for event in normalized_events]
            
            # Import and run the CFP filter agent
            try:
                from . import cfp_filter_agent
                filtered_results = cfp_filter_agent.filter_events(events_for_filtering)
            except ImportError:
                try:
                    # Fallback for standalone execution
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    import cfp_filter_agent
                    filtered_results = cfp_filter_agent.filter_events(events_for_filtering)
                except ImportError:
                    logger.warning("CFP filter agent not yet implemented, returning all events")
                    # For now, return all events until cfp_filter_agent is implemented
                    filtered_results = events_for_filtering
            
            # Convert back to NormalizedEvent objects
            filtered_events = []
            for event_dict in filtered_results:
                # Create NormalizedEvent from dict
                normalized_event = NormalizedEvent(**event_dict)
                normalized_event.is_filtered = True
                filtered_events.append(normalized_event)
            
            # Save filtered events
            filtered_dicts = [asdict(event) for event in filtered_events]
            self._save_events(filtered_dicts, self.filtered_events_file)
            
            logger.info(f"LLM filtering completed: {len(filtered_events)} relevant events selected from {len(normalized_events)}")
            
            return filtered_events
            
        except Exception as e:
            logger.error(f"Event filtering failed: {e}")
            # Return original events if filtering fails
            return normalized_events
    
    def _send_emails(self, filtered_events: List[NormalizedEvent]) -> bool:
        """Send filtered events via email"""
        try:
            logger.info(f"Preparing to send email with {len(filtered_events)} events")
            
            # Convert to dict format for email sender
            events_for_email = [asdict(event) for event in filtered_events]
            
            # Import and run the email sender
            try:
                from . import email_sender
                success = email_sender.send_cfp_email(events_for_email)
                
                if success:
                    logger.info("Email sent successfully")
                    return True
                else:
                    logger.error("Email sending failed")
                    return False
                    
            except ImportError:
                try:
                    # Fallback for standalone execution
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    import email_sender
                    success = email_sender.send_cfp_email(events_for_email)
                    
                    if success:
                        logger.info("Email sent successfully")
                        return True
                    else:
                        logger.error("Email sending failed")
                        return False
                        
                except ImportError:
                    logger.warning("Email sender agent not yet implemented")
                    return False
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _generate_event_id(self, title: str, link: str) -> str:
        """Generate unique ID for event based on title and link"""
        import hashlib
        content = f"{title.strip().lower()}{link.strip()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text fields"""
        if not text:
            return ""
        # Replace newlines and carriage returns with spaces, then normalize whitespace
        cleaned = text.strip().replace('\n', ' ').replace('\r', ' ')
        # Normalize multiple spaces to single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
    
    def _normalize_deadline(self, deadline: str) -> str:
        """Normalize CFP deadline format"""
        if not deadline:
            return ""
        
        # Basic cleanup
        deadline = deadline.strip()
        
        # TODO: Add more sophisticated date parsing and normalization
        # For now, just return cleaned text
        return deadline
    
    def _normalize_tags(self, tags: List[str]) -> List[str]:
        """Normalize and clean tags"""
        if not tags:
            return []
        
        normalized_tags = []
        for tag in tags:
            if tag and isinstance(tag, str):
                # Clean tag and convert to lowercase
                clean_tag = tag.strip().lower()
                if clean_tag and clean_tag not in normalized_tags:
                    normalized_tags.append(clean_tag)
        
        return normalized_tags
    
    def _save_events(self, events: List[Dict], filepath: Path) -> None:
        """Save events to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False, default=str)
            logger.debug(f"Saved {len(events)} events to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save events to {filepath}: {e}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored events"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'raw_events': 0,
            'normalized_events': 0,
            'filtered_events': 0
        }
        
        try:
            if self.raw_events_file.exists():
                with open(self.raw_events_file) as f:
                    raw_events = json.load(f)
                    stats['raw_events'] = len(raw_events)
        except Exception as e:
            logger.debug(f"Could not read raw events: {e}")
        
        try:
            if self.normalized_events_file.exists():
                with open(self.normalized_events_file) as f:
                    normalized_events = json.load(f)
                    stats['normalized_events'] = len(normalized_events)
        except Exception as e:
            logger.debug(f"Could not read normalized events: {e}")
        
        try:
            if self.filtered_events_file.exists():
                with open(self.filtered_events_file) as f:
                    filtered_events = json.load(f)
                    stats['filtered_events'] = len(filtered_events)
        except Exception as e:
            logger.debug(f"Could not read filtered events: {e}")
        
        return stats

def run_pipeline() -> Dict:
    """
    Main function to run the complete CFP Scout pipeline
    This is the interface that main.py will use
    
    Returns:
        Dict with pipeline execution results
    """
    mcp = EventMCP()
    return mcp.process_pipeline()

if __name__ == "__main__":
    # Test the Event MCP agent
    results = run_pipeline()
    
    print("\n" + "="*60)
    print("CFP SCOUT EVENT MCP PIPELINE RESULTS")
    print("="*60)
    print(f"Pipeline Start: {results['pipeline_start']}")
    print(f"Duration: {results['pipeline_duration']}")
    print(f"Scrapers Run: {', '.join(results['scrapers_run'])}")
    print(f"Raw Events: {results['raw_events_count']}")
    print(f"Normalized Events: {results['normalized_events_count']}")
    print(f"Filtered Events: {results['filtered_events_count']}")
    print(f"Emails Sent: {results['emails_sent']}")
    
    if results['errors']:
        print(f"\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Show statistics
    mcp = EventMCP()
    stats = mcp.get_statistics()
    print(f"\nCurrent Storage Statistics:")
    print(f"  Raw Events: {stats['raw_events']}")
    print(f"  Normalized Events: {stats['normalized_events']}")
    print(f"  Filtered Events: {stats['filtered_events']}") 