#!/usr/bin/env python3
"""
🌐 EXAMPLE PLUGIN: Web Scraping
==============================

Example plugin that demonstrates web scraping with structured responses.
Shows how to scrape data and store in cache, files, and database.
"""

import json
import time
import random
from typing import List, Dict, Any


def scrape_website(url: str, selector: str = "title") -> dict:
    """
    Scrape a website and return structured data.
    
    Args:
        url: Website URL to scrape
        selector: CSS selector for elements to extract
    
    Returns:
        Structured plugin response
    """
    
    # Simulate web scraping
    time.sleep(2)  # Simulate network request
    
    # Generate fake scraped data
    scraped_data = {
        "url": url,
        "selector": selector,
        "scraped_at": time.time(),
        "elements": []
    }
    
    # Simulate finding elements
    num_elements = random.randint(5, 20)
    for i in range(num_elements):
        element = {
            "text": f"Sample element {i+1}",
            "href": f"https://example.com/page{i+1}",
            "position": i+1
        }
        scraped_data["elements"].append(element)
    
    if random.random() < 0.9:  # 90% success rate
        response = {
            "status_code": 200,
            "message": f"Successfully scraped {num_elements} elements from {url}",
            "data": [
                {
                    "type": "cache",
                    "name": "last_scrape_url",
                    "value": url
                },
                {
                    "type": "cache",
                    "name": "last_scrape_count", 
                    "value": num_elements
                },
                {
                    "type": "file",
                    "name": f"scrape_{int(time.time())}.json",
                    "value": scraped_data
                },
                {
                    "type": "db",
                    "name": "scrape_summary",
                    "value": {
                        "url": url,
                        "elements_found": num_elements,
                        "scraped_at": time.time(),
                        "status": "success"
                    }
                }
            ]
        }
    else:
        # Failure case
        response = {
            "status_code": 500,
            "message": f"Failed to scrape {url}: Connection timeout",
            "data": [
                {
                    "type": "cache",
                    "name": "last_scrape_error",
                    "value": f"Timeout scraping {url} at {time.time()}"
                },
                {
                    "type": "file",
                    "name": "scrape_errors.log",
                    "value": f"{time.ctime()}: Failed to scrape {url} - Connection timeout\n"
                }
            ]
        }
    
    return response


def batch_scrape(urls: List[str]) -> dict:
    """
    Scrape multiple URLs in batch.
    
    Args:
        urls: List of URLs to scrape
    
    Returns:
        Structured plugin response with batch results
    """
    
    results = []
    successful_scrapes = 0
    failed_scrapes = 0
    
    for url in urls:
        time.sleep(0.5)  # Simulate scraping delay
        
        if random.random() < 0.85:  # 85% success rate per URL
            elements_found = random.randint(1, 15)
            results.append({
                "url": url,
                "status": "success",
                "elements_found": elements_found,
                "scraped_at": time.time()
            })
            successful_scrapes += 1
        else:
            results.append({
                "url": url,
                "status": "failed",
                "error": "Connection timeout",
                "scraped_at": time.time()
            })
            failed_scrapes += 1
    
    batch_summary = {
        "total_urls": len(urls),
        "successful": successful_scrapes,
        "failed": failed_scrapes,
        "results": results,
        "batch_completed_at": time.time()
    }
    
    response = {
        "status_code": 200 if failed_scrapes == 0 else 207,  # 207 = Multi-Status
        "message": f"Batch scrape completed: {successful_scrapes} successful, {failed_scrapes} failed",
        "data": [
            {
                "type": "cache",
                "name": "last_batch_summary",
                "value": batch_summary
            },
            {
                "type": "file",
                "name": f"batch_scrape_{int(time.time())}.json",
                "value": batch_summary
            },
            {
                "type": "db",
                "name": "batch_scrape_results",
                "value": {
                    "batch_id": f"batch_{int(time.time())}",
                    "total_urls": len(urls),
                    "successful": successful_scrapes,
                    "failed": failed_scrapes,
                    "completed_at": time.time()
                }
            }
        ]
    }
    
    return response


def monitor_website(url: str, check_text: str) -> dict:
    """
    Monitor a website for specific text content.
    
    Args:
        url: Website URL to monitor
        check_text: Text to look for on the page
    
    Returns:
        Structured plugin response with monitoring results
    """
    
    # Simulate checking website
    time.sleep(1)
    
    # Simulate finding or not finding the text
    text_found = random.random() < 0.7  # 70% chance of finding text
    
    monitor_result = {
        "url": url,
        "check_text": check_text,
        "text_found": text_found,
        "checked_at": time.time(),
        "status": "up" if text_found else "issue_detected"
    }
    
    if text_found:
        response = {
            "status_code": 200,
            "message": f"Website {url} is healthy - text '{check_text}' found",
            "data": [
                {
                    "type": "cache",
                    "name": f"monitor_{url.replace('://', '_').replace('/', '_')}_status",
                    "value": "healthy"
                },
                {
                    "type": "db",
                    "name": "website_monitor",
                    "value": monitor_result
                }
            ]
        }
    else:
        response = {
            "status_code": 400,
            "message": f"Website {url} issue detected - text '{check_text}' not found",
            "data": [
                {
                    "type": "cache",
                    "name": f"monitor_{url.replace('://', '_').replace('/', '_')}_status",
                    "value": "issue_detected"
                },
                {
                    "type": "file",
                    "name": "website_alerts.log",
                    "value": f"{time.ctime()}: ALERT - {url} - Text '{check_text}' not found\n"
                },
                {
                    "type": "db",
                    "name": "website_alerts",
                    "value": monitor_result
                }
            ]
        }
    
    return response


# Legacy function for backward compatibility
def simple_scrape(url: str) -> str:
    """Simple scraping function that returns a string"""
    elements_found = random.randint(1, 10)
    return f"Scraped {elements_found} elements from {url}"


if __name__ == "__main__":
    # Test the functions
    print("=== Testing Web Scraping Plugin ===\n")
    
    # Test single scrape
    result = scrape_website("https://example.com", "h1")
    print("Single Scrape Response:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test batch scrape
    urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
    result = batch_scrape(urls)
    print("Batch Scrape Response:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test monitoring
    result = monitor_website("https://example.com", "Welcome")
    print("Website Monitor Response:")
    print(json.dumps(result, indent=2))
