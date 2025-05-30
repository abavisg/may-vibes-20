#!/usr/bin/env python3
"""
Scraper MCP Server
Exposes web scraping capabilities via Anthropic's Model Context Protocol
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from pathlib import Path
from datetime import datetime

# Add src directory to path so we can import our existing modules
sys.path.append(str(Path(__file__).parent.parent))

from scraper import scrape_confs_tech_cfp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the MCP server
mcp_server = FastMCP("CFP Scraper Agent")

class ScraperAgent:
    """CFP scraper agent for conference data collection"""
    
    def __init__(self):
        self.last_scrape_time = None
        self.last_scrape_count = 0
        self.total_scrapes = 0
        self.scrape_sources = {
            'confs_tech_cfp': {
                'url': 'https://confs.tech/cfp',
                'active': True,
                'description': 'Conference CFPs from confs.tech'
            }
        }
    
    def scrape_cfp_events(self, sources: List[str] = None) -> Dict:
        """Scrape CFP events from specified sources"""
        try:
            if sources is None:
                sources = ['confs_tech_cfp']
            
            all_events = []
            scrape_results = {}
            
            for source in sources:
                try:
                    if source == 'confs_tech_cfp':
                        events = scrape_confs_tech_cfp()
                        all_events.extend(events)
                        scrape_results[source] = {
                            'success': True,
                            'events_count': len(events),
                            'events': events
                        }
                    else:
                        scrape_results[source] = {
                            'success': False,
                            'error': f'Unknown source: {source}',
                            'events_count': 0,
                            'events': []
                        }
                
                except Exception as e:
                    scrape_results[source] = {
                        'success': False,
                        'error': str(e),
                        'events_count': 0,
                        'events': []
                    }
            
            # Update statistics
            self.last_scrape_time = datetime.now().isoformat()
            self.last_scrape_count = len(all_events)
            self.total_scrapes += 1
            
            return {
                'success': True,
                'total_events': len(all_events),
                'events': all_events,
                'sources_results': scrape_results,
                'scrape_timestamp': self.last_scrape_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'total_events': 0,
                'events': [],
                'sources_results': {},
                'scrape_timestamp': datetime.now().isoformat()
            }
    
    def get_scraper_statistics(self) -> Dict:
        """Get scraper usage statistics"""
        return {
            'total_scrapes': self.total_scrapes,
            'last_scrape_time': self.last_scrape_time,
            'last_scrape_count': self.last_scrape_count,
            'available_sources': list(self.scrape_sources.keys()),
            'active_sources': [k for k, v in self.scrape_sources.items() if v['active']]
        }

# Initialize the scraper agent
scraper_agent = ScraperAgent()

@mcp_server.tool()
async def scrape_cfp_events(sources: list[str] = None) -> dict:
    """
    Scrape CFP events from various conference sources
    
    Args:
        sources: List of source names to scrape (default: ['confs_tech_cfp'])
    
    Returns:
        Scraped events data with metadata
    """
    try:
        if sources is None:
            sources = ['confs_tech_cfp']
        
        result = scraper_agent.scrape_cfp_events(sources)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_events": 0,
            "events": [],
            "sources_results": {}
        }

@mcp_server.tool()
async def get_available_sources() -> dict:
    """Get list of available scraping sources"""
    try:
        return {
            "success": True,
            "sources": scraper_agent.scrape_sources
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sources": {}
        }

@mcp_server.tool()
async def get_scraper_statistics() -> dict:
    """Get scraper usage statistics and performance metrics"""
    try:
        stats = scraper_agent.get_scraper_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "statistics": {}
        }

@mcp_server.tool()
async def test_scraper_connectivity() -> dict:
    """Test connectivity to scraping targets"""
    try:
        import requests
        test_results = {}
        
        for source_name, source_info in scraper_agent.scrape_sources.items():
            try:
                response = requests.head(source_info['url'], timeout=10)
                test_results[source_name] = {
                    "accessible": response.status_code == 200,
                    "status_code": response.status_code,
                    "url": source_info['url']
                }
            except Exception as e:
                test_results[source_name] = {
                    "accessible": False,
                    "error": str(e),
                    "url": source_info['url']
                }
        
        return {
            "success": True,
            "connectivity_results": test_results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "connectivity_results": {}
        }

@mcp_server.resource("scraper://sources")
async def get_scraper_sources() -> str:
    """Get detailed information about available scraping sources"""
    sources_info = {
        "available_sources": scraper_agent.scrape_sources,
        "last_updated": datetime.now().isoformat(),
        "total_sources": len(scraper_agent.scrape_sources)
    }
    return json.dumps(sources_info, indent=2)

@mcp_server.resource("scraper://statistics")
async def get_detailed_statistics() -> str:
    """Get comprehensive scraper statistics"""
    stats = scraper_agent.get_scraper_statistics()
    stats["resource_timestamp"] = datetime.now().isoformat()
    return json.dumps(stats, indent=2)

@mcp_server.resource("scraper://status")
async def get_scraper_status() -> str:
    """Get current scraper status and health"""
    status = {
        "service": "cfp_scraper",
        "status": "ready",
        "total_scrapes_performed": scraper_agent.total_scrapes,
        "last_scrape": scraper_agent.last_scrape_time,
        "available_sources": len(scraper_agent.scrape_sources),
        "health_check": datetime.now().isoformat()
    }
    return json.dumps(status, indent=2)

@mcp_server.resource("scraper://last_results")
async def get_last_scrape_results() -> str:
    """Get results from the most recent scrape operation"""
    if not scraper_agent.last_scrape_time:
        return "No scrapes performed yet"
    
    last_results = {
        "last_scrape_time": scraper_agent.last_scrape_time,
        "events_found": scraper_agent.last_scrape_count,
        "status": "completed" if scraper_agent.last_scrape_count > 0 else "no_events_found"
    }
    return json.dumps(last_results, indent=2)

@mcp_server.prompt()
async def create_scraping_strategy_prompt(target_count: int = 50) -> str:
    """Generate a prompt for optimizing scraping strategies"""
    current_sources = list(scraper_agent.scrape_sources.keys())
    
    prompt = f"""You are optimizing the CFP scraping strategy for CFP Scout.

Current Configuration:
- Active sources: {current_sources}
- Target events per scrape: {target_count}
- Last scrape found: {scraper_agent.last_scrape_count} events

Analyze and suggest improvements for:

1. **Source Diversification**: What additional CFP sources should we add?
   - Conference aggregator sites
   - Developer community platforms  
   - Tech company event pages
   - University and research institution sites

2. **Scraping Frequency**: How often should we scrape each source?
   - High-frequency sources (daily)
   - Medium-frequency sources (weekly)
   - Low-frequency sources (monthly)

3. **Data Quality**: How can we improve event data quality?
   - Better deadline parsing
   - Enhanced location detection
   - Improved tag/category extraction

4. **Performance Optimization**: How can we make scraping more efficient?
   - Parallel processing strategies
   - Caching mechanisms
   - Rate limiting best practices

Provide specific, actionable recommendations."""

    return prompt

@mcp_server.prompt()
async def create_event_validation_prompt(events_data: str) -> str:
    """Generate a prompt for validating scraped event data"""
    prompt = f"""You are validating CFP event data scraped by CFP Scout.

Scraped events data:
{events_data}

Perform data validation and quality assessment:

1. **Completeness Check**: Are all required fields present?
   - Event title
   - CFP deadline
   - Location/format (in-person/virtual)
   - Event URL

2. **Data Quality Assessment**: 
   - Are deadlines in a valid date format?
   - Do URLs appear to be working/valid?
   - Are event titles descriptive and accurate?
   - Is location information clear?

3. **Duplicate Detection**: Are there any duplicate events?

4. **Relevance Scoring**: How relevant are these events for tech professionals?

5. **Recommendations**: What data cleaning or enhancement is needed?

Provide a summary of data quality issues and suggestions for improvement."""

    return prompt

# Main function to run the MCP server
async def main():
    """Run the Scraper MCP Server"""
    try:
        print("🌐 Starting CFP Scraper MCP Server...")
        print(f"📡 Available Sources: {list(scraper_agent.scrape_sources.keys())}")
        print(f"📊 Total Scrapes Performed: {scraper_agent.total_scrapes}")
        
        if scraper_agent.last_scrape_time:
            print(f"🕐 Last Scrape: {scraper_agent.last_scrape_time}")
            print(f"📈 Last Results: {scraper_agent.last_scrape_count} events")
        else:
            print("🆕 No previous scrapes recorded")
        
        # Run the MCP server
        await mcp_server.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        raise

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        # Try to get the existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, just run the server
            asyncio.create_task(main())
        else:
            asyncio.run(main())
    except RuntimeError:
        # No event loop running, create a new one
        asyncio.run(main()) 