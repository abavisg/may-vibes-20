#!/usr/bin/env python3
"""
Event Orchestrator MCP Server
Exposes CFP Scout pipeline coordination capabilities via Anthropic's Model Context Protocol
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

from event_orchestrator import EventOrchestrator, NormalizedEvent, run_pipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the MCP server
mcp_server = FastMCP("Event Orchestrator")

# Initialize the underlying orchestrator
orchestrator = EventOrchestrator()

@mcp_server.tool()
async def run_cfp_pipeline(scraper_modules: list[str] = None) -> dict:
    """
    Execute the complete CFP Scout pipeline
    
    Args:
        scraper_modules: List of scraper module names to run (defaults to ['scraper'])
    
    Returns:
        Pipeline execution results with statistics
    """
    try:
        # Run the existing pipeline
        results = orchestrator.process_pipeline(scraper_modules)
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": {}
        }

@mcp_server.tool()
async def normalize_events(raw_events: list[dict]) -> dict:
    """
    Normalize raw events into consistent data structure
    
    Args:
        raw_events: List of raw event dictionaries from scrapers
    
    Returns:
        Normalized events and statistics
    """
    try:
        normalized_events = orchestrator._normalize_events(raw_events)
        
        # Convert NormalizedEvent objects to dictionaries
        normalized_dicts = []
        for event in normalized_events:
            if isinstance(event, NormalizedEvent):
                # Convert dataclass to dict
                from dataclasses import asdict
                normalized_dicts.append(asdict(event))
            else:
                normalized_dicts.append(event)
        
        return {
            "success": True,
            "normalized_events": normalized_dicts,
            "total_input": len(raw_events),
            "total_normalized": len(normalized_events),
            "duplicates_removed": len(raw_events) - len(normalized_events)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "normalized_events": [],
            "total_input": len(raw_events) if raw_events else 0,
            "total_normalized": 0,
            "duplicates_removed": 0
        }

@mcp_server.tool()
async def get_pipeline_statistics() -> dict:
    """Get current pipeline statistics from stored events"""
    try:
        stats = orchestrator.get_statistics()
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
async def clean_storage() -> dict:
    """Clean up stored event files"""
    try:
        files_removed = []
        
        for file_path in [orchestrator.raw_events_file, 
                         orchestrator.normalized_events_file,
                         orchestrator.filtered_events_file]:
            if file_path.exists():
                file_path.unlink()
                files_removed.append(str(file_path))
        
        return {
            "success": True,
            "files_removed": files_removed,
            "message": f"Cleaned {len(files_removed)} files"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "files_removed": []
        }

@mcp_server.resource("pipeline://status")
async def get_pipeline_status() -> str:
    """Get current pipeline execution status"""
    try:
        stats = orchestrator.get_statistics()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "storage_directory": str(orchestrator.storage_dir),
            "events": {
                "raw": stats.get('raw_events', 0),
                "normalized": stats.get('normalized_events', 0),
                "filtered": stats.get('filtered_events', 0)
            },
            "files": {
                "raw_events_file": str(orchestrator.raw_events_file),
                "normalized_events_file": str(orchestrator.normalized_events_file),
                "filtered_events_file": str(orchestrator.filtered_events_file)
            },
            "file_status": {
                "raw_exists": orchestrator.raw_events_file.exists(),
                "normalized_exists": orchestrator.normalized_events_file.exists(),
                "filtered_exists": orchestrator.filtered_events_file.exists()
            }
        }
        
        return json.dumps(status, indent=2)
        
    except Exception as e:
        return f"Error getting pipeline status: {str(e)}"

@mcp_server.resource("events://raw")
async def get_raw_events() -> str:
    """Get all raw events from storage"""
    try:
        if orchestrator.raw_events_file.exists():
            with open(orchestrator.raw_events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            return json.dumps(events, indent=2)
        else:
            return "No raw events file found"
    except Exception as e:
        return f"Error reading raw events: {str(e)}"

@mcp_server.resource("events://normalized")
async def get_normalized_events() -> str:
    """Get all normalized events from storage"""
    try:
        if orchestrator.normalized_events_file.exists():
            with open(orchestrator.normalized_events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            return json.dumps(events, indent=2)
        else:
            return "No normalized events file found"
    except Exception as e:
        return f"Error reading normalized events: {str(e)}"

@mcp_server.resource("events://filtered")
async def get_filtered_events() -> str:
    """Get all filtered events from storage"""
    try:
        if orchestrator.filtered_events_file.exists():
            with open(orchestrator.filtered_events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            return json.dumps(events, indent=2)
        else:
            return "No filtered events file found"
    except Exception as e:
        return f"Error reading filtered events: {str(e)}"

@mcp_server.resource("events://normalized/{event_id}")
async def get_normalized_event_by_id(event_id: str) -> str:
    """Get a specific normalized event by ID"""
    try:
        if orchestrator.normalized_events_file.exists():
            with open(orchestrator.normalized_events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            for event in events:
                if event.get('id') == event_id:
                    return json.dumps(event, indent=2)
            
            return f"Event with ID '{event_id}' not found"
        else:
            return "No normalized events file found"
    except Exception as e:
        return f"Error reading event {event_id}: {str(e)}"

@mcp_server.prompt()
async def create_pipeline_execution_prompt() -> str:
    """Generate a prompt for pipeline execution planning"""
    current_stats = orchestrator.get_statistics()
    
    prompt = f"""You are the CFP Scout Event Orchestrator. Plan the execution of the CFP discovery pipeline.

Current Status:
- Raw Events: {current_stats.get('raw_events', 0)}
- Normalized Events: {current_stats.get('normalized_events', 0)}
- Filtered Events: {current_stats.get('filtered_events', 0)}

Available Pipeline Steps:
1. Scrape CFP events from confs.tech/cfp
2. Normalize and deduplicate events
3. Filter events using Ollama LLM based on user interests
4. Send email notifications with filtered results

Plan the optimal execution strategy considering:
- Data freshness requirements
- Processing time constraints
- Resource availability
- Error handling

Provide a step-by-step execution plan."""

    return prompt

@mcp_server.prompt()
async def create_event_analysis_prompt(event_count: int) -> str:
    """Generate a prompt for analyzing discovered events"""
    prompt = f"""You are analyzing {event_count} CFP events discovered by CFP Scout.

Please analyze the events and provide insights on:

1. **Geographic Distribution**: Where are most conferences located?
2. **Topic Trends**: What are the most common conference topics/themes?
3. **Timeline Analysis**: When are most CFP deadlines?
4. **Relevance Assessment**: How well do these align with typical tech interests?
5. **Quality Indicators**: Are there any standout conferences?

Provide a comprehensive analysis that helps users understand the conference landscape and make informed decisions about which CFPs to pursue."""

    return prompt

# Main function to run the MCP server
async def main():
    """Run the Event Orchestrator MCP Server"""
    try:
        print("🎼 Starting Event Orchestrator MCP Server...")
        print(f"📁 Storage Directory: {orchestrator.storage_dir}")
        
        # Show current statistics
        stats = orchestrator.get_statistics()
        print(f"📊 Current Stats:")
        print(f"   Raw Events: {stats.get('raw_events', 0)}")
        print(f"   Normalized Events: {stats.get('normalized_events', 0)}")
        print(f"   Filtered Events: {stats.get('filtered_events', 0)}")
        
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