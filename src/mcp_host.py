#!/usr/bin/env python3
"""
CFP Scout MCP Host
Main MCP client that coordinates communication between CFP Scout agents via Model Context Protocol
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import mcp.types as types
except ImportError:
    print("❌ MCP package not found. Please install it with: pip install mcp")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CFPScoutMCPHost:
    """
    Main MCP host for CFP Scout system
    Coordinates communication between agents via Model Context Protocol
    """
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.server_processes = {}
        
        # Agent server configurations
        self.server_configs = {
            'event_orchestrator': StdioServerParameters(
                command='python3',
                args=[str(Path(__file__).parent / 'agents' / 'event_orchestrator_mcp_server.py')]
            ),
            'cfp_filter': StdioServerParameters(
                command='python3',
                args=[str(Path(__file__).parent / 'agents' / 'cfp_filter_mcp_server.py')]
            )
        }
        
        logger.info("CFP Scout MCP Host initialized")
        logger.info(f"Available agents: {list(self.server_configs.keys())}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_agent_servers()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop_agent_servers()
    
    async def start_agent_servers(self):
        """Initialize all MCP agent servers"""
        logger.info("🚀 Starting MCP agent servers...")
        
        for name, config in self.server_configs.items():
            try:
                logger.info(f"   Starting {name} server...")
                
                # Start the server process
                read_stream, write_stream = await stdio_client(config).__aenter__()
                
                # Create client session
                session = ClientSession(read_stream, write_stream)
                await session.initialize()
                
                self.sessions[name] = session
                logger.info(f"   ✅ {name} server started successfully")
                
                # List available tools for debugging
                try:
                    tools = await session.list_tools()
                    tool_names = [tool.name for tool in tools]
                    logger.info(f"      Available tools: {tool_names}")
                except Exception as e:
                    logger.warning(f"      Could not list tools: {e}")
                
            except Exception as e:
                logger.error(f"   ❌ Failed to start {name} server: {e}")
                # Continue with other servers
                continue
        
        logger.info(f"✅ Started {len(self.sessions)} out of {len(self.server_configs)} agent servers")
    
    async def stop_agent_servers(self):
        """Stop all MCP agent servers"""
        logger.info("🛑 Stopping MCP agent servers...")
        
        for name, session in self.sessions.items():
            try:
                # Sessions will be cleaned up automatically
                logger.info(f"   Stopped {name} server")
            except Exception as e:
                logger.warning(f"   Error stopping {name} server: {e}")
        
        self.sessions.clear()
        logger.info("✅ All agent servers stopped")
    
    async def execute_pipeline_via_mcp(self, scraper_modules: List[str] = None) -> Dict:
        """
        Execute CFP Scout pipeline using MCP tool calls
        
        Args:
            scraper_modules: List of scraper modules to run
        
        Returns:
            Pipeline execution results
        """
        logger.info("🎯 Executing CFP Scout pipeline via MCP...")
        
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'stages': {},
            'success': False,
            'errors': []
        }
        
        try:
            # Stage 1: Run complete pipeline via Event Orchestrator
            if 'event_orchestrator' in self.sessions:
                logger.info("   Stage 1: Running complete pipeline...")
                
                orchestrator_result = await self.sessions['event_orchestrator'].call_tool(
                    'run_cfp_pipeline',
                    {'scraper_modules': scraper_modules or ['scraper']}
                )
                
                pipeline_results['stages']['orchestrator'] = orchestrator_result
                
                if orchestrator_result.get('success'):
                    logger.info("   ✅ Pipeline execution completed successfully")
                    
                    # Get detailed statistics
                    stats_result = await self.sessions['event_orchestrator'].call_tool(
                        'get_pipeline_statistics', {}
                    )
                    pipeline_results['stages']['statistics'] = stats_result
                    
                else:
                    logger.error(f"   ❌ Pipeline execution failed: {orchestrator_result.get('error')}")
                    pipeline_results['errors'].append(orchestrator_result.get('error', 'Unknown error'))
            
            else:
                error_msg = "Event Orchestrator server not available"
                logger.error(f"   ❌ {error_msg}")
                pipeline_results['errors'].append(error_msg)
            
            # Stage 2: Test CFP Filter independently (if available)
            if 'cfp_filter' in self.sessions:
                logger.info("   Stage 2: Testing CFP Filter connection...")
                
                filter_test_result = await self.sessions['cfp_filter'].call_tool(
                    'test_ollama_connection', {}
                )
                
                pipeline_results['stages']['filter_test'] = filter_test_result
                
                if filter_test_result.get('success') and filter_test_result.get('ollama_connected'):
                    logger.info("   ✅ CFP Filter is ready")
                else:
                    logger.warning("   ⚠️ CFP Filter connection issues")
            
            # Mark as successful if at least the main pipeline ran
            if pipeline_results['stages'].get('orchestrator', {}).get('success'):
                pipeline_results['success'] = True
            
        except Exception as e:
            error_msg = f"Pipeline execution error: {e}"
            logger.error(f"   ❌ {error_msg}")
            pipeline_results['errors'].append(error_msg)
        
        finally:
            pipeline_results['end_time'] = datetime.now().isoformat()
        
        return pipeline_results
    
    async def get_pipeline_status(self) -> Dict:
        """Get current pipeline status from Event Orchestrator"""
        try:
            if 'event_orchestrator' not in self.sessions:
                return {"error": "Event Orchestrator not available"}
            
            # Get pipeline status via resource
            status_resource = await self.sessions['event_orchestrator'].read_resource(
                'pipeline://status'
            )
            
            return {
                "success": True,
                "status": json.loads(status_resource)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_interests(self) -> Dict:
        """Get user interests from CFP Filter"""
        try:
            if 'cfp_filter' not in self.sessions:
                return {"error": "CFP Filter not available"}
            
            # Get user interests via resource
            interests_resource = await self.sessions['cfp_filter'].read_resource(
                'user://interests'
            )
            
            return {
                "success": True,
                "interests": interests_resource
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_all_available_tools(self) -> Dict:
        """List all tools available across all connected servers"""
        all_tools = {}
        
        for server_name, session in self.sessions.items():
            try:
                tools = await session.list_tools()
                all_tools[server_name] = [
                    {
                        "name": tool.name,
                        "description": tool.description
                    }
                    for tool in tools
                ]
            except Exception as e:
                all_tools[server_name] = {"error": str(e)}
        
        return all_tools
    
    async def list_all_available_resources(self) -> Dict:
        """List all resources available across all connected servers"""
        all_resources = {}
        
        for server_name, session in self.sessions.items():
            try:
                resources = await session.list_resources()
                all_resources[server_name] = [
                    {
                        "uri": resource.uri,
                        "name": resource.name,
                        "description": resource.description,
                        "mimeType": resource.mimeType
                    }
                    for resource in resources
                ]
            except Exception as e:
                all_resources[server_name] = {"error": str(e)}
        
        return all_resources

# Main demonstration function
async def main():
    """Demonstrate CFP Scout MCP Host functionality"""
    
    print("🌟 CFP Scout MCP Host Demonstration")
    print("=" * 60)
    
    try:
        async with CFPScoutMCPHost() as mcp_host:
            
            # Show available tools and resources
            print("\n📋 Available Tools:")
            tools = await mcp_host.list_all_available_tools()
            for server, server_tools in tools.items():
                print(f"   {server}:")
                if isinstance(server_tools, list):
                    for tool in server_tools:
                        print(f"     - {tool['name']}: {tool['description']}")
                else:
                    print(f"     Error: {server_tools}")
            
            print("\n📚 Available Resources:")
            resources = await mcp_host.list_all_available_resources()
            for server, server_resources in resources.items():
                print(f"   {server}:")
                if isinstance(server_resources, list):
                    for resource in server_resources:
                        print(f"     - {resource['uri']}: {resource.get('description', 'No description')}")
                else:
                    print(f"     Error: {server_resources}")
            
            # Get current pipeline status
            print("\n📊 Current Pipeline Status:")
            status = await mcp_host.get_pipeline_status()
            if status.get('success'):
                status_data = status['status']
                events = status_data.get('events', {})
                print(f"   Raw Events: {events.get('raw', 0)}")
                print(f"   Normalized Events: {events.get('normalized', 0)}")
                print(f"   Filtered Events: {events.get('filtered', 0)}")
            else:
                print(f"   Error: {status.get('error', 'Unknown error')}")
            
            # Get user interests
            print("\n🎯 User Interests:")
            interests = await mcp_host.get_user_interests()
            if interests.get('success'):
                print(f"   {interests['interests']}")
            else:
                print(f"   Error: {interests.get('error', 'Unknown error')}")
            
            # Execute the pipeline
            print("\n🚀 Executing CFP Scout Pipeline via MCP...")
            results = await mcp_host.execute_pipeline_via_mcp()
            
            print("\n📈 Pipeline Results:")
            print(f"   Success: {results['success']}")
            print(f"   Start Time: {results['start_time']}")
            print(f"   End Time: {results['end_time']}")
            
            if results['errors']:
                print(f"   Errors: {results['errors']}")
            
            # Show stage results
            for stage_name, stage_result in results['stages'].items():
                print(f"   {stage_name.title()}: {stage_result.get('success', 'N/A')}")
            
    except Exception as e:
        print(f"❌ MCP Host demonstration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 