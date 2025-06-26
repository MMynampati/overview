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
        import langchain
        import langchain_openai
        import langchain_community
        print("langchain modules imported successfully")
    except ImportError as e:
        print(f"Failed to import langchain modules: {e}")
        return False
    
    try:
        import sentence_transformers
        print("sentence_transformers imported successfully")
    except ImportError as e:
        print(f"Failed to import sentence_transformers: {e}")
        return False
    
    return True

def test_core_modules():
    """Test if core modules can be imported and initialized."""
    print("\nTesting core modules...")
    
    try:
        from core.crawler import load_urls_from_csv, scrape_url_list, setup_driver
        print("core.crawler functions imported successfully")
    except ImportError as e:
        print(f"Failed to import core.crawler: {e}")
        return False
    
    try:
        # Check if the CSV file exists
        if os.path.exists("core/overview.csv"):
            print("CSV file found")
        else:
            print("CSV file not found")
            return False
    except Exception as e:
        print(f"Failed to check CSV file: {e}")
        return False
    
    return True

def test_ingestion_pipeline():
    """Test if the ingestion pipeline can be imported."""
    print("\nTesting ingestion pipeline...")
    
    try:
        import ingest
        print("ingest module imported successfully")
    except ImportError as e:
        print(f"Failed to import ingest module: {e}")
        return False
    
    return True

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

def test_documentation_access():
    """Test if documentation site is accessible."""
    print("\nTesting documentation access...")
    
    try:
        import requests
        from core.crawler import HEADERS
        
        # Test the landing page
        response = requests.get("https://docs.overview.ai/docs/start-here", headers=HEADERS, timeout=10)
        response.raise_for_status()
        print("Documentation site is accessible")
        return True
    except Exception as e:
        print(f"Documentation access failed: {e}")
        return False

def main():
    print("Testing Manual Pages Search Interface Setup")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", test_env_variables),
        ("Module Imports", test_imports),
        ("Core Modules", test_core_modules),
        ("Ingestion Pipeline", test_ingestion_pipeline),
        ("OpenAI Connection", test_openai_connection),
        ("Documentation Access", test_documentation_access)
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
        print("1. Run ingestion: python ingest.py")
        print("2. Run application: streamlit run app.py")
        print("3. Or run with Docker: docker-compose up --build")
    else:
        print("Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 