#!/usr/bin/env python3
"""
Setup script for Manual Pages Search Interface
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return
    
    # Copy env.example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("📝 Please edit .env file with your configuration:")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import openai
        import requests
        import chromadb
        import langchain
        import langchain_openai
        import langchain_community
        import sentence_transformers
        print("✅ All required dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_core_modules():
    """Check if core modules can be imported."""
    try:
        from core.crawler import get_urls_from_sitemap
        from core.loader import WebContentLoader
        print("✅ Core modules are available")
        return True
    except ImportError as e:
        print(f"❌ Missing core module: {e}")
        return False

def create_data_directory():
    """Create data directory for vector database."""
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    print("✅ Data directory ready")

def main():
    print("🚀 Setting up Manual Pages Search Interface")
    print("=" * 50)
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check core modules
    if not check_core_modules():
        sys.exit(1)
    
    # Create data directory
    create_data_directory()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your OpenAI API key and sitemap URL")
    print("2. Run ingestion: python ingest.py")
    print("3. Run application: streamlit run app.py")
    print("4. Or run with Docker: docker-compose up --build")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 