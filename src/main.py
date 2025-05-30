#!/usr/bin/env python3
"""
CFP Scout Main Orchestration Script
Handles scheduled execution of the CFP discovery pipeline with MCP support
"""

import asyncio
import argparse
import logging
import os
import sys
import time
import schedule
import pytz
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cfp_scout_main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CFPScoutOrchestrator:
    """
    Main orchestrator for CFP Scout pipeline execution
    Supports both traditional and MCP execution modes
    """
    
    def __init__(self, execution_mode: str = "hybrid"):
        self.execution_mode = execution_mode  # "traditional", "mcp", "hybrid"
        self.schedule_time = os.getenv('SCHEDULE_TIME', '08:00')
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Europe/London'))
        self.last_execution = None
        self.execution_count = 0
        self.total_events_processed = 0
        
        # Ensure logs directory exists
        Path('logs').mkdir(exist_ok=True)
        
        logger.info(f"CFP Scout Orchestrator initialized in {execution_mode} mode")
        logger.info(f"Scheduled for daily execution at {self.schedule_time} {self.timezone}")
    
    async def execute_traditional_pipeline(self) -> Dict:
        """Execute CFP Scout using traditional pipeline"""
        logger.info("🔄 Executing traditional pipeline...")
        
        try:
            from event_orchestrator import EventOrchestrator
            
            orchestrator = EventOrchestrator()
            results = orchestrator.process_pipeline()
            
            return {
                'success': True,
                'mode': 'traditional',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Traditional pipeline failed: {e}")
            return {
                'success': False,
                'mode': 'traditional',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def execute_mcp_pipeline(self) -> Dict:
        """Execute CFP Scout using MCP agent ecosystem"""
        logger.info("🌐 Executing MCP pipeline...")
        
        try:
            from mcp_host import CFPScoutMCPHost
            
            async with CFPScoutMCPHost() as mcp_host:
                # Execute full MCP pipeline
                results = await mcp_host.execute_full_mcp_pipeline()
                
                return {
                    'success': results.get('success', False),
                    'mode': 'mcp',
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"MCP pipeline failed: {e}")
            return {
                'success': False,
                'mode': 'mcp',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def execute_hybrid_pipeline(self) -> Dict:
        """Execute CFP Scout using hybrid approach (MCP coordination + traditional execution)"""
        logger.info("🔀 Executing hybrid pipeline...")
        
        try:
            from mcp_host import CFPScoutMCPHost
            
            async with CFPScoutMCPHost() as mcp_host:
                # Execute traditional pipeline with MCP coordination
                results = await mcp_host.execute_pipeline_via_mcp()
                
                return {
                    'success': results.get('success', False),
                    'mode': 'hybrid',
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.warning(f"Hybrid pipeline failed, falling back to traditional: {e}")
            # Fallback to traditional pipeline
            return await self.execute_traditional_pipeline()
    
    async def execute_pipeline(self) -> Dict:
        """Execute the CFP Scout pipeline based on configured mode"""
        start_time = datetime.now()
        logger.info(f"🚀 Starting CFP Scout pipeline execution (mode: {self.execution_mode})")
        
        try:
            # Execute based on mode
            if self.execution_mode == "traditional":
                results = await self.execute_traditional_pipeline()
            elif self.execution_mode == "mcp":
                results = await self.execute_mcp_pipeline()
            elif self.execution_mode == "hybrid":
                results = await self.execute_hybrid_pipeline()
            else:
                raise ValueError(f"Unknown execution mode: {self.execution_mode}")
            
            # Update statistics
            end_time = datetime.now()
            duration = end_time - start_time
            
            self.last_execution = end_time
            self.execution_count += 1
            
            # Extract event counts if available
            events_processed = 0
            if results.get('success') and results.get('results'):
                pipeline_results = results['results']
                if isinstance(pipeline_results, dict):
                    # For traditional/hybrid mode
                    stats = pipeline_results.get('statistics', {})
                    if isinstance(stats, dict) and 'statistics' in stats:
                        events_processed = stats['statistics'].get('filtered_events', 0)
                    # For MCP mode
                    elif 'stages' in pipeline_results:
                        filtering_stage = pipeline_results['stages'].get('filtering', {})
                        events_processed = filtering_stage.get('total_filtered', 0)
            
            self.total_events_processed += events_processed
            
            # Log results
            if results.get('success'):
                logger.info(f"✅ Pipeline execution completed successfully")
                logger.info(f"📊 Mode: {results['mode']}, Duration: {duration.total_seconds():.2f}s")
                logger.info(f"📈 Events processed: {events_processed}")
                logger.info(f"📋 Total executions: {self.execution_count}")
            else:
                logger.error(f"❌ Pipeline execution failed: {results.get('error', 'Unknown error')}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Critical error in pipeline execution: {e}")
            return {
                'success': False,
                'mode': self.execution_mode,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def schedule_daily_execution(self):
        """Set up daily scheduled execution"""
        logger.info(f"⏰ Scheduling daily execution at {self.schedule_time}")
        
        # Schedule the job
        schedule.every().day.at(self.schedule_time).do(self._run_scheduled_job)
        
        logger.info("📅 Scheduler started. Waiting for scheduled time...")
        
        # Run scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _run_scheduled_job(self):
        """Run the scheduled job (sync wrapper for async execution)"""
        logger.info("⏰ Scheduled execution triggered")
        
        try:
            # Run the async pipeline
            results = asyncio.run(self.execute_pipeline())
            
            if results.get('success'):
                logger.info("✅ Scheduled execution completed successfully")
            else:
                logger.error("❌ Scheduled execution failed")
                
        except Exception as e:
            logger.error(f"❌ Scheduled execution error: {e}")
    
    def get_status(self) -> Dict:
        """Get current orchestrator status"""
        return {
            'execution_mode': self.execution_mode,
            'schedule_time': self.schedule_time,
            'timezone': str(self.timezone),
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_count': self.execution_count,
            'total_events_processed': self.total_events_processed,
            'next_scheduled': self._get_next_scheduled_time()
        }
    
    def _get_next_scheduled_time(self) -> Optional[str]:
        """Get next scheduled execution time"""
        try:
            jobs = schedule.get_jobs()
            if jobs:
                return jobs[0].next_run.isoformat()
            return None
        except:
            return None

def main():
    """Main entry point with command line argument support"""
    parser = argparse.ArgumentParser(description='CFP Scout Main Orchestrator')
    parser.add_argument(
        '--mode', 
        choices=['traditional', 'mcp', 'hybrid'], 
        default='hybrid',
        help='Execution mode (default: hybrid)'
    )
    parser.add_argument(
        '--run-once', 
        action='store_true',
        help='Run once instead of scheduling'
    )
    parser.add_argument(
        '--schedule', 
        action='store_true',
        help='Run in scheduled mode (default if no other option specified)'
    )
    parser.add_argument(
        '--status', 
        action='store_true',
        help='Show current status and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = CFPScoutOrchestrator(execution_mode=args.mode)
    
    if args.status:
        # Show status
        print("📊 CFP Scout Orchestrator Status")
        print("=" * 50)
        status = orchestrator.get_status()
        for key, value in status.items():
            print(f"{key}: {value}")
        return
    
    if args.run_once:
        # Run once
        print("🚀 Running CFP Scout pipeline once...")
        results = asyncio.run(orchestrator.execute_pipeline())
        
        if results.get('success'):
            print("✅ Execution completed successfully")
        else:
            print(f"❌ Execution failed: {results.get('error')}")
            sys.exit(1)
    
    else:
        # Default: run in scheduled mode
        print("⏰ Starting CFP Scout scheduled execution...")
        orchestrator.schedule_daily_execution()

if __name__ == "__main__":
    main() 