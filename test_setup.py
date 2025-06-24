#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Manual Pages Search Interface
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_env_variables():
    """Test if environment variables are properly set."""
    load_dotenv()
    
    print("Testing environment variables...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OPENAI_API_KEY not found")
        return False
    elif api_key == 'your_openai_api_key_here':
        print("OPENAI_API_KEY is still set to placeholder value")
        return False
    else:
        print("OPENAI_API_KEY is configured")
    
    manual_pages = os.getenv('MANUAL_PAGES')
    if not manual_pages:
        print("MANUAL_PAGES not found")
        return False
    elif 'example.com' in manual_pages:
        print("MANUAL_PAGES still contains example URLs")
        return False
    else:
        print("MANUAL_PAGES is configured")
    
    return True

def test_imports():
    """Test if all required modules can be imported."""
    print("\nTesting imports...")
    
    try:
        import streamlit
        print("streamlit imported successfully")
    except ImportError as e:
        print(f"Failed to import streamlit: {e}")
        return False
    
    try:
        import openai
        print("openai imported successfully")
    except ImportError as e:
        print(f"Failed to import openai: {e}")
        return False
    
    try:
        import chromadb
        print("chromadb imported successfully")
    except ImportError as e:
        print(f"Failed to import chromadb: {e}")
        return False
    
    try:
        from scraper import ManualPageScraper
        print("ManualPageScraper imported successfully")
    except ImportError as e:
        print(f"Failed to import ManualPageScraper: {e}")
        return False
    
    return True

def test_scraper_initialization():
    """Test if the scraper can be initialized."""
    print("\nTesting scraper initialization...")
    
    try:
        from scraper import ManualPageScraper
        scraper = ManualPageScraper()
        print("ManualPageScraper initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize ManualPageScraper: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    print("\nTesting OpenAI connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("OpenAI API connection successful")
        return True
    except Exception as e:
        print(f"OpenAI API connection failed: {e}")
        return False

def main():
    print("Testing Manual Pages Search Interface Setup")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_env_variables),
        ("Module Imports", test_imports),
        ("Scraper Initialization", test_scraper_initialization),
        ("OpenAI Connection", test_openai_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"{test_name} test failed")
        except Exception as e:
            print(f"{test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Or run with Docker: docker-compose up --build")
    else:
        print("Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 