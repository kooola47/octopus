#!/usr/bin/env python3
"""
Test NLP processor with new plugin hints
"""
import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from nlp_processor import get_nlp_processor

def test_nlp_improvements():
    """Test the NLP processor with our new plugin hints"""
    processor = get_nlp_processor()
    
    print("=== Testing NLP Processor with Plugin Hints ===\n")
    
    # Test file operations
    test_cases = [
        "create file report.txt with content hello world",
        "read file config.json with max 50 lines", 
        "list directory /var/log including hidden files",
        "process numbers 1,2,3,4,5 with sum operation",
        "calculate math expression 2 + 3 * 4",
        "generate 10 random numbers between 1 and 100",
        "send notification to admin about server outage",
        "get system information and CPU usage",
        "check url status for https://google.com",
        "validate email address admin@company.com"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}: {test_input}")
        try:
            result = processor.parse_natural_language(test_input)
            print(f"Plugin: {result.get('task', {}).get('plugin', 'Unknown')}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
            print(f"Parameters: {result.get('task', {}).get('parameters', {})}")
            print("-" * 60)
        except Exception as e:
            print(f"Error: {e}")
            print("-" * 60)
        print()

if __name__ == "__main__":
    test_nlp_improvements()
