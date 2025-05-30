#!/usr/bin/env python3
"""
CFP Filter Agent for CFP Scout
Uses Ollama locally to filter and score CFP events based on user interests
Works with Event Orchestrator to process normalized events
"""

import json
import logging
import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CFPFilterAgent:
    """
    CFP Filter Agent using Ollama for local LLM-based event filtering
    """
    
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3:latest')
        self.user_interests = self._parse_user_interests()
        
        logger.info(f"CFP Filter Agent initialized with Ollama at {self.ollama_host}")
        logger.info(f"Using model: {self.ollama_model}")
        logger.info(f"User interests: {', '.join(self.user_interests)}")
    
    def _parse_user_interests(self) -> List[str]:
        """Parse user interests and preferences from environment variables"""
        # Get event themes (main interests)
        themes_str = os.getenv('EVENT_THEMES', os.getenv('USER_INTERESTS', ''))
        if not themes_str:
            logger.warning("No EVENT_THEMES or USER_INTERESTS found in environment, using defaults")
            return ['AI', 'machine learning', 'software engineering']
        
        # Parse themes
        themes = [theme.strip() for theme in themes_str.split(',')]
        themes = [theme for theme in themes if theme]
        
        # Get location preferences
        locations_str = os.getenv('EVENT_LOCATIONS', '')
        if locations_str:
            locations = [loc.strip() for loc in locations_str.split(',')]
            locations = [loc for loc in locations if loc]
            themes.extend([f"events in {loc}" for loc in locations])
        
        # Get event type preferences
        event_types_str = os.getenv('EVENT_TYPE', '')
        if event_types_str:
            event_types = [etype.strip() for etype in event_types_str.split(',')]
            event_types = [etype for etype in event_types if etype]
            themes.extend([f"{etype.lower()} events" for etype in event_types])
        
        return themes
    
    def _test_ollama_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.ollama_model in model_names:
                    logger.info(f"✅ Ollama connection successful, model {self.ollama_model} available")
                    return True
                else:
                    logger.warning(f"⚠️ Model {self.ollama_model} not found. Available models: {model_names}")
                    return False
            else:
                logger.error(f"❌ Ollama API returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Cannot connect to Ollama at {self.ollama_host}: {e}")
            return False
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Make API call to Ollama"""
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent results
                    "top_p": 0.9,
                    "num_predict": 100   # Limit response length
                }
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None
    
    def _score_event_relevance(self, event: Dict) -> float:
        """Score an event's relevance to user interests using Ollama"""
        try:
            # Prepare event context for LLM
            event_context = f"""
Event Title: {event.get('title', 'Unknown')}
Location: {event.get('location', 'Unknown')}
Topics/Tags: {', '.join(event.get('tags', []))}
Description: {event.get('description', 'No description available')}
CFP Deadline: {event.get('cfp_deadline', 'Unknown')}
"""
            
            # Create more specific prompt for relevance scoring with detailed criteria
            user_interests_str = ', '.join(self.user_interests)
            prompt = f"""Analyze this conference CFP for relevance to specific interests, locations, and event types.

USER PREFERENCES: {user_interests_str}

CONFERENCE DETAILS:
{event_context}

ANALYSIS TASK:
Compare the conference against ALL user preferences including:
1. Topic relevance (AI, machine learning, DevOps, etc.)
2. Location preferences (Europe, UK, Online, etc.)
3. Event format preferences (Online, Physical)

ENHANCED SCORING CRITERIA:
- Perfect match (topic + location + format) = 0.9-1.0
- Topic + location match = 0.7-0.9
- Topic + format match = 0.6-0.8
- Topic match only = 0.5-0.7
- Location/format only = 0.2-0.4
- No clear relevance = 0.0-0.2

EXAMPLES:
- AI Conference in London (Online) for user wanting "AI, Europe, Online" → 0.95
- DevOps event in Berlin for user wanting "DevOps, Europe" → 0.8
- PHP Conference in Asia for user wanting "AI, Europe" → 0.1

Output ONLY the numerical score (e.g., 0.8) with NO other text."""

            response = self._call_ollama(prompt)
            
            # Debug: Print what Ollama actually returned
            logger.debug(f"Ollama response for '{event.get('title', 'Unknown')}': '{response}'")
            
            if response:
                # Try to extract a number from the response
                import re
                # Look for decimal numbers between 0 and 1
                number_match = re.search(r'([0-1]\.?\d*)', response.strip())
                if number_match:
                    score = float(number_match.group(1))
                    # Ensure score is between 0.0 and 1.0
                    score = max(0.0, min(1.0, score))
                    logger.debug(f"Event '{event.get('title', 'Unknown')}' scored {score}")
                    return score
                else:
                    logger.warning(f"Could not parse score from Ollama response: '{response}' for event: {event.get('title', 'Unknown')}")
                    return 0.5  # Default to neutral score
            else:
                logger.warning(f"No response from Ollama for event: {event.get('title', 'Unknown')}")
                return 0.5  # Default to neutral score
                
        except Exception as e:
            logger.error(f"Error scoring event relevance: {e}")
            return 0.5  # Default to neutral score
    
    def filter_events(self, events: List[Dict], min_score: float = 0.6) -> List[Dict]:
        """
        Filter events based on relevance to user interests
        
        Args:
            events: List of normalized event dictionaries
            min_score: Minimum relevance score to include event (0.0-1.0)
        
        Returns:
            List of filtered events with relevance scores
        """
        if not events:
            logger.info("No events to filter")
            return []
        
        # Test Ollama connection first
        if not self._test_ollama_connection():
            logger.error("Cannot connect to Ollama, returning all events unfiltered")
            # Return all events with default score
            for event in events:
                event['relevance_score'] = 0.5
                event['is_filtered'] = True
            return events
        
        logger.info(f"Starting LLM filtering of {len(events)} events with min_score={min_score}")
        
        filtered_events = []
        
        for i, event in enumerate(events):
            try:
                # Score the event
                relevance_score = self._score_event_relevance(event)
                event['relevance_score'] = relevance_score
                
                # Filter based on score
                if relevance_score >= min_score:
                    event['is_filtered'] = True
                    filtered_events.append(event)
                    logger.info(f"✅ Event {i+1}/{len(events)}: '{event.get('title', 'Unknown')}' - Score: {relevance_score:.2f}")
                else:
                    logger.debug(f"❌ Event {i+1}/{len(events)}: '{event.get('title', 'Unknown')}' - Score: {relevance_score:.2f} (below threshold)")
                
            except Exception as e:
                logger.error(f"Error filtering event {i+1}: {e}")
                # Include event with default score on error
                event['relevance_score'] = 0.5
                event['is_filtered'] = True
                filtered_events.append(event)
        
        logger.info(f"LLM filtering completed: {len(filtered_events)} relevant events selected from {len(events)} total")
        
        # Sort by relevance score (highest first)
        filtered_events.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered_events
    
    def get_filter_summary(self, original_events: List[Dict], filtered_events: List[Dict]) -> Dict:
        """Generate a summary of the filtering results"""
        summary = {
            'total_events': len(original_events),
            'filtered_events': len(filtered_events),
            'filter_ratio': len(filtered_events) / len(original_events) if original_events else 0,
            'avg_score': 0,
            'score_distribution': {
                'high_relevance': 0,     # 0.8+
                'medium_relevance': 0,   # 0.6-0.8
                'low_relevance': 0       # <0.6
            }
        }
        
        if filtered_events:
            scores = [event.get('relevance_score', 0) for event in filtered_events]
            summary['avg_score'] = sum(scores) / len(scores)
            
            for score in scores:
                if score >= 0.8:
                    summary['score_distribution']['high_relevance'] += 1
                elif score >= 0.6:
                    summary['score_distribution']['medium_relevance'] += 1
                else:
                    summary['score_distribution']['low_relevance'] += 1
        
        return summary

def filter_events(events: List[Dict], min_score: float = 0.6) -> List[Dict]:
    """
    Main function to filter CFP events - this is the interface other modules will use
    
    Args:
        events: List of normalized event dictionaries
        min_score: Minimum relevance score to include event (0.0-1.0)
    
    Returns:
        List of filtered events with relevance scores
    """
    filter_agent = CFPFilterAgent()
    return filter_agent.filter_events(events, min_score)

if __name__ == "__main__":
    # Test the CFP Filter Agent
    print("🧠 Testing CFP Filter Agent with Ollama")
    print("=" * 50)
    
    # Test with some sample events
    sample_events = [
        {
            'title': 'AI & Machine Learning Conference 2025',
            'cfp_deadline': 'June 15',
            'location': 'San Francisco, CA',
            'tags': ['ai', 'machine learning', 'data science'],
            'link': 'https://aiconf2025.com',
            'description': 'Premier conference for AI researchers and practitioners',
            'source': 'test'
        },
        {
            'title': 'DevOps World 2025',
            'cfp_deadline': 'July 1',
            'location': 'Online',
            'tags': ['devops', 'cloud', 'automation'],
            'link': 'https://devopsworld.com',
            'description': 'The largest DevOps conference for cloud and automation',
            'source': 'test'
        },
        {
            'title': 'PHP Conference 2025',
            'cfp_deadline': 'May 30',
            'location': 'Berlin, Germany',
            'tags': ['php', 'web development'],
            'link': 'https://phpconf.com',
            'description': 'Annual PHP conference for web developers',
            'source': 'test'
        }
    ]
    
    try:
        filter_agent = CFPFilterAgent()
        
        # Test connection
        if filter_agent._test_ollama_connection():
            print("✅ Ollama connection successful!")
            
            # Filter events
            filtered = filter_agent.filter_events(sample_events, min_score=0.6)
            
            print(f"\nFiltering Results:")
            print(f"Original events: {len(sample_events)}")
            print(f"Filtered events: {len(filtered)}")
            
            print("\nFiltered Events:")
            for i, event in enumerate(filtered):
                score = event.get('relevance_score', 0)
                print(f"{i+1}. {event['title']} - Score: {score:.2f}")
            
            # Show summary
            summary = filter_agent.get_filter_summary(sample_events, filtered)
            print(f"\nSummary:")
            print(f"Filter ratio: {summary['filter_ratio']:.1%}")
            print(f"Average score: {summary['avg_score']:.2f}")
            print(f"Score distribution: {summary['score_distribution']}")
            
        else:
            print("❌ Could not connect to Ollama")
            print("Make sure Ollama is running with: ollama serve")
            print(f"And that the model {filter_agent.ollama_model} is available")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise 