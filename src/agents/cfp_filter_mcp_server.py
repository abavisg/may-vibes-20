#!/usr/bin/env python3
"""
CFP Filter MCP Server
Exposes CFP filtering capabilities via Anthropic's Model Context Protocol
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from pathlib import Path

# Add src directory to path so we can import our existing modules
sys.path.append(str(Path(__file__).parent.parent))

from cfp_filter_agent import CFPFilterAgent, filter_events
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the MCP server
mcp_server = FastMCP("CFP Filter Agent")

# Initialize the underlying filter agent
filter_agent = CFPFilterAgent()

@mcp_server.tool()
async def filter_cfp_events(events: list[dict], min_score: float = 0.6) -> list[dict]:
    """
    Filter CFP events based on user interests using Ollama LLM
    
    Args:
        events: List of normalized event dictionaries
        min_score: Minimum relevance score to include event (0.0-1.0)
    
    Returns:
        List of filtered events with relevance scores
    """
    try:
        # Call the existing filter agent
        filtered_events = filter_agent.filter_events(events, min_score)
        
        return {
            "success": True,
            "filtered_events": filtered_events,
            "total_original": len(events),
            "total_filtered": len(filtered_events),
            "filter_ratio": len(filtered_events) / len(events) if events else 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filtered_events": [],
            "total_original": len(events),
            "total_filtered": 0,
            "filter_ratio": 0
        }

@mcp_server.tool()
async def test_ollama_connection() -> dict:
    """Test if Ollama is running and accessible"""
    try:
        is_connected = filter_agent._test_ollama_connection()
        return {
            "success": True,
            "ollama_connected": is_connected,
            "ollama_host": filter_agent.ollama_host,
            "ollama_model": filter_agent.ollama_model
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "ollama_connected": False
        }

@mcp_server.tool()
async def get_filter_summary(original_events: list[dict], filtered_events: list[dict]) -> dict:
    """Generate a summary of filtering results"""
    try:
        summary = filter_agent.get_filter_summary(original_events, filtered_events)
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "summary": {}
        }

@mcp_server.resource("user://interests")
async def get_user_interests() -> str:
    """Get current user interests configuration"""
    interests = filter_agent.user_interests
    return f"Current user interests: {', '.join(interests)}"

@mcp_server.resource("ollama://status")
async def get_ollama_status() -> str:
    """Get Ollama connection and model status"""
    try:
        is_connected = filter_agent._test_ollama_connection()
        status = {
            "host": filter_agent.ollama_host,
            "model": filter_agent.ollama_model,
            "connected": is_connected,
            "status": "online" if is_connected else "offline"
        }
        return json.dumps(status, indent=2)
    except Exception as e:
        return f"Error checking Ollama status: {str(e)}"

@mcp_server.resource("config://filter")
async def get_filter_config() -> str:
    """Get current filter configuration"""
    config = {
        "ollama_host": filter_agent.ollama_host,
        "ollama_model": filter_agent.ollama_model,
        "user_interests": filter_agent.user_interests,
        "default_min_score": 0.6
    }
    return json.dumps(config, indent=2)

@mcp_server.prompt()
async def create_filter_prompt(event_title: str, event_description: str) -> str:
    """Generate a filtering prompt for manual LLM evaluation"""
    interests = ', '.join(filter_agent.user_interests)
    
    prompt = f"""You are a conference recommendation system. Rate how relevant this conference CFP is to someone interested in: {interests}.

Event Title: {event_title}
Event Description: {event_description}

Rate the relevance on a scale of 0.0 to 1.0 where:
- 0.0 = Not relevant at all
- 0.3 = Somewhat relevant 
- 0.6 = Moderately relevant
- 0.8 = Highly relevant
- 1.0 = Extremely relevant

Consider the conference title and description. Look for matches with the user's interests.

Respond with ONLY a number between 0.0 and 1.0, nothing else."""

    return prompt

@mcp_server.prompt()
async def create_batch_filter_prompt(events_json: str) -> str:
    """Generate a prompt for batch filtering multiple events"""
    interests = ', '.join(filter_agent.user_interests)
    
    prompt = f"""You are a conference recommendation system. Filter these CFP events based on relevance to someone interested in: {interests}.

Events to evaluate:
{events_json}

For each event, provide a relevance score from 0.0 to 1.0 and include only events with score >= 0.6.

Return the results as JSON with this structure:
{{
  "filtered_events": [
    {{
      "title": "Event Title",
      "relevance_score": 0.8,
      "reason": "Brief explanation of relevance"
    }}
  ]
}}"""

    return prompt

# Main function to run the MCP server
async def main():
    """Run the CFP Filter MCP Server"""
    try:
        print("🧠 Starting CFP Filter MCP Server...")
        print(f"📡 Ollama Host: {filter_agent.ollama_host}")
        print(f"🤖 Model: {filter_agent.ollama_model}")
        print(f"🎯 User Interests: {', '.join(filter_agent.user_interests)}")
        
        # Test Ollama connection on startup
        if filter_agent._test_ollama_connection():
            print("✅ Ollama connection successful!")
        else:
            print("⚠️ Warning: Could not connect to Ollama")
        
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