#!/usr/bin/env python3
"""
Download dependencies for LAN Excel Editor
"""
import os
import urllib.request
import ssl

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

FILES = [
    {
        'url': 'https://cdn.jsdelivr.net/npm/handsontable@14.3.0/dist/handsontable.full.min.css',
        'path': 'static/css/handsontable.full.min.css',
        'desc': 'Handsontable CSS'
    },
    {
        'url': 'https://cdn.jsdelivr.net/npm/handsontable@14.3.0/dist/handsontable.full.min.js',
        'path': 'static/js/handsontable.full.min.js',
        'desc': 'Handsontable JS'
    },
    {
        'url': 'https://cdn.socket.io/4.7.5/socket.io.min.js',
        'path': 'static/js/socket.io.min.js',
        'desc': 'Socket.io JS'
    }
]

def download_file(url, filepath, description):
    """Download a single file"""
    try:
        print(f"Downloading: {description}")
        print(f"  URL: {url}")
        print(f"  Save to: {filepath}")
        
        # Create directory
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Download file
        urllib.request.urlretrieve(url, filepath)
        
        # Get file size
        size = os.path.getsize(filepath)
        print(f"  OK ({size:,} bytes)\n")
        return True
        
    except Exception as e:
        print(f"  FAILED: {e}\n")
        return False

def main():
    print("=" * 60)
    print("LAN Excel Editor - Dependency Downloader")
    print("=" * 60)
    print()
    
    success_count = 0
    fail_count = 0
    
    for file_info in FILES:
        if download_file(file_info['url'], file_info['path'], file_info['desc']):
            success_count += 1
        else:
            fail_count += 1
    
    print("=" * 60)
    print(f"Download complete: {success_count} success, {fail_count} failed")
    print("=" * 60)
    
    if fail_count > 0:
        print("\nSome files failed to download. Please check your network connection.")
        print("Or manually download these files:")
        for file_info in FILES:
            if not os.path.exists(file_info['path']):
                print(f"  - {file_info['url']} -> {file_info['path']}")
    else:
        print("\nAll dependencies downloaded to static/ directory")
        print("You can now start the server!")

if __name__ == '__main__':
    main()