#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Overview AI Chatbot
Tests both deployment-ready setup and full development setup
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_warning(msg):
    print(f"⚠️ {msg}")

def print_info(msg):
    print(f"ℹ️ {msg}")

def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description}: {filepath} (NOT FOUND)")
        return False

def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print_success(f"{description}: {module_name}")
        return True
    except ImportError as e:
        print_error(f"{description}: {module_name} - {e}")
        return False

def test_python_version():
    """Test Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python version: {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def test_environment_variables():
    """Test environment variables"""
    print_header("Environment Variables")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print_success(f"OPENAI_API_KEY: {'*' * (len(openai_key) - 4) + openai_key[-4:]}")
    else:
        print_warning("OPENAI_API_KEY not set (will need for full testing)")
    
    return openai_key is not None

def test_deployment_setup():
    """Test the deployment-ready setup in src/"""
    print_header("Testing Deployment Setup (src/)")
    
    tests_passed = 0
    total_tests = 0
    
    # Test file structure
    total_tests += 1
    if test_file_exists("src/app.py", "Streamlit app"):
        tests_passed += 1
    
    total_tests += 1
    if test_file_exists("src/requirements.txt", "Requirements file"):
        tests_passed += 1
    
    total_tests += 1
    if test_file_exists("src/vectorstore", "Vector database directory"):
        tests_passed += 1
    
    # Test if vectorstore has content
    total_tests += 1
    if os.path.exists("src/vectorstore") and len(os.listdir("src/vectorstore")) > 0:
        print_success("Vector database has content")
        tests_passed += 1
    else:
        print_error("Vector database is empty")
    
    # Test imports from requirements
    print_info("Testing deployment dependencies...")
    deployment_deps = [
        ("streamlit", "Streamlit"),
        ("openai", "OpenAI"),
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_community", "LangChain Community"),
        ("python-dotenv", "Python-dotenv"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers")
    ]
    
    for module, description in deployment_deps:
        total_tests += 1
        if test_import(module, description):
            tests_passed += 1
    
    print_info(f"Deployment setup: {tests_passed}/{total_tests} tests passed")
    return tests_passed, total_tests

def test_development_setup():
    """Test the full development setup"""
    print_header("Testing Development Setup")
    
    tests_passed = 0
    total_tests = 0
    
    # Test development files
    total_tests += 1
    if test_file_exists("core/crawler.py", "Web crawler"):
        tests_passed += 1
    
    total_tests += 1
    if test_file_exists("ingest.py", "Data ingestion script"):
        tests_passed += 1
    
    total_tests += 1
    if test_file_exists("full_requirements.txt", "Full requirements"):
        tests_passed += 1
    
    total_tests += 1
    if test_file_exists("env.example", "Environment template"):
        tests_passed += 1
    
    # Test if scraped data exists
    total_tests += 1
    if test_file_exists("core/overview.csv", "Scraped data"):
        print_success("Scraped data found")
        tests_passed += 1
    else:
        print_warning("No scraped data found (run crawler.py first)")
    
    print_info(f"Development setup: {tests_passed}/{total_tests} tests passed")
    return tests_passed, total_tests

def test_streamlit_app():
    """Test if the Streamlit app can be imported and initialized"""
    print_header("Testing Streamlit App")
    
    try:
        # Change to src directory
        original_dir = os.getcwd()
        os.chdir("src")
        
        # Test app import
        import app
        print_success("App module imported successfully")
        
        # Test if components can be loaded
        if hasattr(app, 'load_components'):
            print_success("App has load_components function")
        
        # Test if vectorstore path is correct
        if hasattr(app, 'DB_PATH'):
            db_path = app.DB_PATH
            if os.path.exists(db_path):
                print_success(f"Vector database found at: {db_path}")
            else:
                print_error(f"Vector database not found at: {db_path}")
        
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print_error(f"Failed to test Streamlit app: {e}")
        os.chdir(original_dir)
        return False

def run_streamlit_test():
    """Actually run Streamlit to test the app"""
    print_header("Running Streamlit Test")
    
    try:
        # Change to src directory
        original_dir = os.getcwd()
        os.chdir("src")
        
        print_info("Starting Streamlit app for testing...")
        print_info("This will open a browser window. Close it when done testing.")
        
        # Run streamlit in a subprocess
        process = subprocess.Popen(
            ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8502"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for it to start
        import time
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print_success("Streamlit app started successfully")
            print_info("App should be available at: http://localhost:8502")
            print_info("Press Ctrl+C to stop the test")
            
            try:
                process.wait(timeout=30)  # Wait up to 30 seconds
            except subprocess.TimeoutExpired:
                print_info("Stopping Streamlit app...")
                process.terminate()
                process.wait()
        else:
            stdout, stderr = process.communicate()
            print_error(f"Streamlit failed to start: {stderr.decode()}")
        
        os.chdir(original_dir)
        return True
        
    except KeyboardInterrupt:
        print_info("Test interrupted by user")
        if 'process' in locals():
            process.terminate()
        os.chdir(original_dir)
        return True
    except Exception as e:
        print_error(f"Failed to run Streamlit test: {e}")
        os.chdir(original_dir)
        return False

def main():
    """Run all tests"""
    print_header("Overview AI Chatbot - Complete Test Suite")
    
    # Basic environment tests
    print_header("Basic Environment")
    test_python_version()
    has_openai_key = test_environment_variables()
    
    # Test deployment setup
    deploy_passed, deploy_total = test_deployment_setup()
    
    # Test development setup
    dev_passed, dev_total = test_development_setup()
    
    # Test Streamlit app
    app_works = test_streamlit_app()
    
    # Summary
    print_header("Test Summary")
    print_info(f"Deployment Setup: {deploy_passed}/{deploy_total} tests passed")
    print_info(f"Development Setup: {dev_passed}/{dev_total} tests passed")
    print_info(f"Streamlit App: {'✅ Working' if app_works else '❌ Failed'}")
    
    if has_openai_key:
        print_info("OpenAI API key found - ready for full testing")
        
        # Ask if user wants to run Streamlit test
        response = input("\n🤔 Do you want to run the Streamlit app test? (y/n): ")
        if response.lower() in ['y', 'yes']:
            run_streamlit_test()
    else:
        print_warning("No OpenAI API key - some features won't work")
    
    print_header("Testing Complete!")
    print_info("Next steps:")
    print_info("1. For deployment: Upload src/ to Streamlit Cloud")
    print_info("2. For local use: cd src && streamlit run app.py")
    print_info("3. For development: Follow README.md instructions")

if __name__ == "__main__":
    main() 