#!/usr/bin/env python3
"""
Test script for Event Orchestrator Agent
Tests core functionality including deduplication, normalization, and data flow
"""

import json
import tempfile
from pathlib import Path
from event_orchestrator import EventOrchestrator, NormalizedEvent

def test_deduplication():
    """Test that duplicate events are properly handled"""
    print("Testing Event Orchestrator deduplication...")
    
    # Create test events with some duplicates
    test_events = [
        {
            'title': 'Test Conference A',
            'cfp_deadline': 'June 1',
            'location': 'Berlin, Germany',
            'tags': ['ai', 'tech'],
            'link': 'https://testconf-a.com',
            'description': 'Test description',
            'source': 'test',
            'scraped_at': '2025-05-30T12:00:00'
        },
        {
            'title': 'Test Conference B',
            'cfp_deadline': 'July 15',
            'location': 'Online',
            'tags': ['devops'],
            'link': 'https://testconf-b.com',
            'description': 'Another test',
            'source': 'test',
            'scraped_at': '2025-05-30T12:00:00'
        },
        # Duplicate of first event (same title and link)
        {
            'title': 'Test Conference A',
            'cfp_deadline': 'June 1',
            'location': 'Berlin, Germany',
            'tags': ['ai', 'tech'],
            'link': 'https://testconf-a.com',
            'description': 'Test description',
            'source': 'test',
            'scraped_at': '2025-05-30T12:01:00'  # Different timestamp
        }
    ]
    
    # Create temporary orchestrator instance
    with tempfile.TemporaryDirectory() as temp_dir:
        orchestrator = EventOrchestrator(storage_dir=temp_dir)
        
        # Normalize events
        normalized = orchestrator._normalize_events(test_events)
        
        # Should have only 2 unique events (duplicate removed)
        assert len(normalized) == 2, f"Expected 2 unique events, got {len(normalized)}"
        
        # Check that the normalized events have the expected titles
        titles = [event.title for event in normalized]
        assert 'Test Conference A' in titles
        assert 'Test Conference B' in titles
        
        print(f"✅ Deduplication test passed: {len(test_events)} → {len(normalized)} events")
        
        # Test statistics
        stats = orchestrator.get_statistics()
        assert stats['normalized_events'] == 2
        print(f"✅ Statistics test passed: {stats}")

def test_event_id_generation():
    """Test that event IDs are generated consistently"""
    print("\nTesting Event ID generation...")
    
    orchestrator = EventOrchestrator()
    
    # Same title and link should generate same ID
    id1 = orchestrator._generate_event_id("Test Conference", "https://test.com")
    id2 = orchestrator._generate_event_id("Test Conference", "https://test.com")
    assert id1 == id2, "Same title and link should generate same ID"
    
    # Different title or link should generate different ID
    id3 = orchestrator._generate_event_id("Different Conference", "https://test.com")
    id4 = orchestrator._generate_event_id("Test Conference", "https://different.com")
    assert id1 != id3, "Different title should generate different ID"
    assert id1 != id4, "Different link should generate different ID"
    
    # Case insensitive and trimming
    id5 = orchestrator._generate_event_id(" TEST CONFERENCE ", "https://test.com")
    assert id1 == id5, "ID generation should be case insensitive and trim whitespace"
    
    print("✅ Event ID generation test passed")

def test_text_cleaning():
    """Test text cleaning functionality"""
    print("\nTesting text cleaning...")
    
    orchestrator = EventOrchestrator()
    
    # Test various text cleaning scenarios
    test_cases = [
        ("  Normal text  ", "Normal text"),
        ("Text\nwith\nnewlines", "Text with newlines"),
        ("Text\rwith\rcarriage\rreturns", "Text with carriage returns"),
        ("", ""),
        (None, "")
    ]
    
    for input_text, expected in test_cases:
        result = orchestrator._clean_text(input_text)
        assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_text}'"
    
    print("✅ Text cleaning test passed")

def test_tag_normalization():
    """Test tag normalization"""
    print("\nTesting tag normalization...")
    
    orchestrator = EventOrchestrator()
    
    # Test tag normalization scenarios
    test_cases = [
        (["AI", "Machine Learning", "ai"], ["ai", "machine learning"]),  # Deduplication and lowercase
        (["  DevOps  ", "SECURITY", ""], ["devops", "security"]),  # Trimming and empty removal
        ([], []),  # Empty list
        ([None, "", "Valid"], ["valid"])  # None and empty string handling
    ]
    
    for input_tags, expected in test_cases:
        result = orchestrator._normalize_tags(input_tags)
        assert result == expected, f"Expected {expected}, got {result} for input {input_tags}"
    
    print("✅ Tag normalization test passed")

if __name__ == "__main__":
    print("🧪 Running Event Orchestrator Agent Tests")
    print("=" * 50)
    
    try:
        test_deduplication()
        test_event_id_generation()
        test_text_cleaning()
        test_tag_normalization()
        
        print("\n" + "=" * 50)
        print("🎉 All Event Orchestrator tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise 