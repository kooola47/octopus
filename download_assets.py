#!/usr/bin/env python3
"""
Download static assets for Octopus Dashboard
===========================================

This script downloads external CSS and font files to the local static directory
so we can serve them locally instead of using CDN links.
"""

import os
import requests
import sys
from pathlib import Path

def download_file(url, local_path, headers=None):
    """Download a file from URL to local path"""
    try:
        print(f"Downloading {url}...")
        
        # Default headers for font downloads
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # Write content to file
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded to {local_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def main():
    """Download all required assets"""
    # Base directories
    project_root = Path(__file__).parent
    static_dir = project_root / "octopus_server" / "static"
    css_dir = static_dir / "css"
    fonts_dir = static_dir / "fonts"
    js_dir = static_dir / "js"
    
    print("🐙 Octopus Dashboard Asset Downloader")
    print("=" * 40)
    
    # Files to download
    downloads = [
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
            "path": css_dir / "bootstrap.min.css"
        },
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
            "path": js_dir / "bootstrap.bundle.min.js"
        },
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css",
            "path": css_dir / "bootstrap-icons.css"
        },
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2",
            "path": fonts_dir / "bootstrap-icons.woff2"
        },
        {
            "url": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff",
            "path": fonts_dir / "bootstrap-icons.woff"
        }
    ]
    
    # Add Inter font files from Google Fonts API
    # We'll download the CSS first to get the actual font URLs
    inter_css_url = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    downloads.append({
        "url": inter_css_url,
        "path": css_dir / "inter.css"
    })
    
    # Download specific Inter font files from GitHub repository
    inter_fonts = [
        {
            "url": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Light.woff2",
            "path": fonts_dir / "Inter-Light.woff2"
        },
        {
            "url": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.woff2", 
            "path": fonts_dir / "Inter-Regular.woff2"
        },
        {
            "url": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Medium.woff2",
            "path": fonts_dir / "Inter-Medium.woff2"
        },
        {
            "url": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-SemiBold.woff2",
            "path": fonts_dir / "Inter-SemiBold.woff2"
        },
        {
            "url": "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.woff2",
            "path": fonts_dir / "Inter-Bold.woff2"
        }
    ]
    
    downloads.extend(inter_fonts)
    
    # Create directories
    css_dir.mkdir(parents=True, exist_ok=True)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    # Download files
    success_count = 0
    total_count = len(downloads)
    
    for download in downloads:
        # Use special headers for Google Fonts
        headers = None
        if "fonts.googleapis.com" in download["url"]:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        
        if download_file(download["url"], download["path"], headers):
            success_count += 1
    
    print("\n" + "=" * 40)
    print(f"Download Summary: {success_count}/{total_count} files downloaded successfully")
    
    if success_count == total_count:
        print("🎉 All assets downloaded successfully!")
        print("\nNext steps:")
        print("1. Update your HTML templates to use local paths:")
        print("   - /static/css/bootstrap.min.css")
        print("   - /static/css/bootstrap-icons.css")
        print("   - /static/css/inter.css")
        print("2. All fonts (Bootstrap Icons and Inter) are now local")
        print("3. You may need to update the inter.css file to point to local font files")
    else:
        print("⚠️  Some downloads failed. Check your internet connection and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
