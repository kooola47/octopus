#!/usr/bin/env python3
"""
Web Utils Plugin
================
Plugin for web-related utilities and HTTP operations

# NLP: keywords: fetch url, http request, web scraping, api call, download, post request, get request
# NLP: example: Fetch URL https://api.github.com/users/octocat with GET method
# NLP: example: Make HTTP request to status page with 60 second timeout
# NLP: example: Download content from website and check response
# NLP: example: POST data to API endpoint with JSON payload
"""

import requests
import urllib.parse
import json
from typing import Optional, Dict, Any
import time

def fetch_url(url: str, method: str = "GET", timeout: int = 30, follow_redirects: bool = True):
    """
    Fetch content from a URL.
    
    # NLP: keywords: fetch url, get url, http get, download webpage, api request
    # NLP: example: Fetch URL https://httpbin.org/get with 45 second timeout
    # NLP: example: Get content from API endpoint with POST method
    
    Args:
        url: URL to fetch
        method: HTTP method (GET, POST, HEAD)
        timeout: Request timeout in seconds (default: 30)
        follow_redirects: Whether to follow redirects (default: True)
    
    Returns:
        str: Response content and metadata
    """
    try:
        method = method.upper()
        
        if method not in ["GET", "POST", "HEAD"]:
            return f"Error: Unsupported HTTP method '{method}'. Use GET, POST, or HEAD"
        
        response = requests.request(
            method=method,
            url=url,
            timeout=timeout,
            allow_redirects=follow_redirects
        )
        
        result = f"URL: {url}\n"
        result += f"Method: {method}\n"
        result += f"Status Code: {response.status_code}\n"
        result += f"Content Type: {response.headers.get('content-type', 'Unknown')}\n"
        result += f"Content Length: {len(response.content)} bytes\n"
        
        if method != "HEAD":
            # Only show content for non-HEAD requests
            content_type = response.headers.get('content-type', '').lower()
            if 'json' in content_type:
                try:
                    json_data = response.json()
                    result += f"\nJSON Response:\n{json.dumps(json_data, indent=2)}"
                except:
                    result += f"\nContent:\n{response.text[:1000]}..."
            else:
                result += f"\nContent:\n{response.text[:1000]}..."
                if len(response.text) > 1000:
                    result += "\n(truncated...)"
        
        return result
        
    except requests.exceptions.Timeout:
        return f"Error: Request to {url} timed out after {timeout} seconds"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to {url}"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

def check_url_status(urls: str, timeout: int = 10):
    """
    Check the status of multiple URLs.
    
    # NLP: keywords: check url status, url health check, website status, ping urls, monitor websites
    # NLP: example: Check URL status for https://google.com,https://github.com with 15 second timeout
    # NLP: example: Monitor website status for production and staging URLs
    
    Args:
        urls: Comma-separated list of URLs to check
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        str: Status report for all URLs
    """
    try:
        url_list = [url.strip() for url in urls.split(',')]
        
        result = f"URL Status Check ({len(url_list)} URLs):\n\n"
        
        for url in url_list:
            try:
                start_time = time.time()
                response = requests.head(url, timeout=timeout, allow_redirects=True)
                response_time = (time.time() - start_time) * 1000
                
                result += f"✓ {url}\n"
                result += f"  Status: {response.status_code}\n"
                result += f"  Response Time: {response_time:.0f}ms\n"
                result += f"  Server: {response.headers.get('server', 'Unknown')}\n\n"
                
            except requests.exceptions.Timeout:
                result += f"✗ {url}\n"
                result += f"  Error: Timeout after {timeout}s\n\n"
            except requests.exceptions.ConnectionError:
                result += f"✗ {url}\n"
                result += f"  Error: Connection failed\n\n"
            except Exception as e:
                result += f"✗ {url}\n"
                result += f"  Error: {str(e)}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error checking URL status: {str(e)}"

def encode_decode_url(text: str, operation: str = "encode"):
    """
    URL encode or decode text.
    
    # NLP: keywords: url encode, url decode, percent encoding, escape url, unescape url
    # NLP: example: URL encode text "hello world space" 
    # NLP: example: Decode URL "%20%3D%26" to readable text
    
    Args:
        text: Text to encode/decode
        operation: Operation to perform (encode, decode)
    
    Returns:
        str: Encoded/decoded result
    """
    try:
        operation = operation.lower()
        
        if operation == "encode":
            result = urllib.parse.quote(text)
            return f"Original: {text}\nURL Encoded: {result}"
        elif operation == "decode":
            result = urllib.parse.unquote(text)
            return f"Original: {text}\nURL Decoded: {result}"
        else:
            return f"Error: Unknown operation '{operation}'. Use 'encode' or 'decode'"
        
    except Exception as e:
        return f"Error processing URL encoding: {str(e)}"

def parse_url(url: str):
    """
    Parse a URL into its components.
    
    # NLP: keywords: parse url, url components, break down url, analyze url
    # NLP: example: Parse URL https://example.com/path?param=value#section
    # NLP: example: Break down URL components for API endpoint
    
    Args:
        url: URL to parse
    
    Returns:
        str: URL components breakdown
    """
    try:
        parsed = urllib.parse.urlparse(url)
        
        result = f"URL: {url}\n\n"
        result += f"Components:\n"
        result += f"  Scheme: {parsed.scheme}\n"
        result += f"  Netloc: {parsed.netloc}\n"
        result += f"  Path: {parsed.path}\n"
        result += f"  Params: {parsed.params}\n"
        result += f"  Query: {parsed.query}\n"
        result += f"  Fragment: {parsed.fragment}\n"
        
        # Parse query parameters
        if parsed.query:
            query_params = urllib.parse.parse_qs(parsed.query)
            result += f"\nQuery Parameters:\n"
            for key, values in query_params.items():
                result += f"  {key}: {', '.join(values)}\n"
        
        return result
        
    except Exception as e:
        return f"Error parsing URL: {str(e)}"

def generate_qr_code(text: str, format_type: str = "text"):
    """
    Generate a simple text-based QR code representation.
    
    # NLP: keywords: generate qr code, create qr code, qr code url, barcode
    # NLP: example: Generate QR code for text "Hello World" with URL format
    # NLP: example: Create QR code for website link in text format
    
    Args:
        text: Text to encode in QR code
        format_type: Output format (text, url)
    
    Returns:
        str: QR code information or URL
    """
    try:
        # For demonstration, we'll provide QR code service URLs
        encoded_text = urllib.parse.quote(text)
        
        if format_type.lower() == "url":
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_text}"
            return f"QR Code URL for '{text}':\n{qr_url}"
        else:
            result = f"QR Code Data: {text}\n"
            result += f"Encoded Length: {len(text)} characters\n"
            result += f"QR Code Service URL: https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_text}\n"
            result += "\nNote: Use the URL above to generate an actual QR code image"
            return result
        
    except Exception as e:
        return f"Error generating QR code: {str(e)}"

def validate_email(email: str):
    """
    Basic email address validation.
    
    # NLP: keywords: validate email, check email, email validation, verify email address
    # NLP: example: Validate email address user@company.com
    # NLP: example: Check if admin@example.org is valid email format
    
    Args:
        email: Email address to validate
    
    Returns:
        str: Validation result
    """
    try:
        import re
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            # Split email into parts
            local, domain = email.split('@')
            
            result = f"Email: {email}\n"
            result += f"Status: ✓ Valid format\n"
            result += f"Local part: {local}\n"
            result += f"Domain: {domain}\n"
            result += f"TLD: {domain.split('.')[-1]}\n"
            
            return result
        else:
            return f"Email: {email}\nStatus: ✗ Invalid format"
        
    except Exception as e:
        return f"Error validating email: {str(e)}"

def shorten_url_info(url: str):
    """
    Provide information about URL shortening (demonstration).
    
    Args:
        url: URL to get shortening info for
    
    Returns:
        str: URL shortening information
    """
    try:
        result = f"URL: {url}\n"
        result += f"Original Length: {len(url)} characters\n"
        
        # Simulate shortening info
        if len(url) > 50:
            result += f"Recommended: Yes (long URL)\n"
        else:
            result += f"Recommended: No (already short)\n"
        
        result += "\nPopular URL Shortening Services:\n"
        result += "  - bit.ly\n"
        result += "  - tinyurl.com\n"
        result += "  - goo.gl (deprecated)\n"
        result += "  - t.co (Twitter)\n"
        
        result += f"\nNote: Use a URL shortening service API for actual shortening"
        
        return result
        
    except Exception as e:
        return f"Error processing URL shortening info: {str(e)}"
