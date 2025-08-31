#!/usr/bin/env python3
"""
Async Demo Plugin
=================

Plugin demonstrating async function support in the Octopus system.

# NLP: keywords: async function, asynchronous, demo, example
# NLP: example: Run async demo function
# NLP: example: Execute async demo with delay
"""

import asyncio
import time

async def async_demo(delay: float = 1.0):
    """
    Demo async function that waits for a specified delay.
    
    # NLP: keywords: async demo, wait, delay, asynchronous function
    # NLP: example: Run async demo with 2 second delay
    # NLP: example: Execute async demo function
    
    Args:
        delay: Number of seconds to wait (default: 1.0)
    
    Returns:
        str: Completion message
    """
    start_time = time.time()
    await asyncio.sleep(delay)
    end_time = time.time()
    return f"Async function completed after {delay} seconds (actual time: {end_time - start_time:.2f}s)"

async def fetch_data(url: str = "https://httpbin.org/delay/1"):
    """
    Demo async function that simulates fetching data from a URL.
    
    # NLP: keywords: fetch data, async fetch, http request, network request
    # NLP: example: Fetch data from example.com
    # NLP: example: Run async fetch data function
    
    Args:
        url: URL to fetch data from (default: https://httpbin.org/delay/1)
    
    Returns:
        str: Simulated response data
    """
    # Simulate network delay
    await asyncio.sleep(1)
    return f"Async fetched data from {url}"

def sync_demo(delay: float = 1.0):
    """
    Demo sync function for comparison.
    
    # NLP: keywords: sync demo, synchronous function, delay
    # NLP: example: Run sync demo with 2 second delay
    # NLP: example: Execute sync demo function
    
    Args:
        delay: Number of seconds to wait (default: 1.0)
    
    Returns:
        str: Completion message
    """
    start_time = time.time()
    time.sleep(delay)
    end_time = time.time()
    return f"Sync function completed after {delay} seconds (actual time: {end_time - start_time:.2f}s)"