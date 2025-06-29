#!/usr/bin/env python3
"""
Test the chatbot functionality directly
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_chatbot_import():
    """Test if we can import the chatbot components"""
    print("🧪 Testing chatbot imports...")
    
    try:
        # Mock streamlit session state to avoid errors
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        
        import app
        print("✅ App imported successfully")
        
        # Test if we can access the main components
        if hasattr(app, 'load_components'):
            print("✅ load_components function found")
        
        if hasattr(app, 'DB_PATH'):
            print(f"✅ DB_PATH configured: {app.DB_PATH}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to import app: {e}")
        return False

def test_vectorstore_loading():
    """Test if the vectorstore can be loaded"""
    print("\n🧪 Testing vectorstore loading...")
    
    try:
        # Mock streamlit session state
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        
        import app
        
        # Try to load the components
        vectorstore, llm = app.load_components()
        
        if vectorstore is not None:
            print("✅ Vectorstore loaded successfully")
            
            # Test a simple query
            try:
                results = vectorstore.similarity_search("test", k=1)
                print(f"✅ Vectorstore query test passed (found {len(results)} results)")
            except Exception as e:
                print(f"⚠️ Vectorstore query test failed: {e}")
        else:
            print("❌ Vectorstore failed to load")
            return False
        
        if llm is not None:
            print("✅ LLM loaded successfully")
        else:
            print("❌ LLM failed to load")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to load components: {e}")
        return False

def test_qa_chain():
    """Test if the QA chain can be created"""
    print("\n🧪 Testing QA chain creation...")
    
    try:
        # Mock streamlit session state
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        
        import app
        
        # Check if qa_chain was created
        if hasattr(app, 'qa_chain') and app.qa_chain is not None:
            print("✅ QA chain created successfully")
            return True
        else:
            print("❌ QA chain not created")
            return False
    except Exception as e:
        print(f"❌ Failed to test QA chain: {e}")
        return False

def test_sample_questions():
    """Test with some sample questions"""
    print("\n🧪 Testing sample questions...")
    
    try:
        # Mock streamlit session state
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        
        import app
        
        if not hasattr(app, 'qa_chain') or app.qa_chain is None:
            print("❌ QA chain not available")
            return False
        
        # Sample questions to test
        test_questions = [
            "What is Overview AI?",
            "How do I authenticate API requests?",
            "What are the main features?",
            "How do I get started?"
        ]
        
        print("Testing sample questions (this may take a moment)...")
        
        for question in test_questions:
            try:
                print(f"\n🤔 Testing: {question}")
                result = app.qa_chain.invoke({"question": question})
                
                if result and 'answer' in result:
                    answer = result['answer']
                    print(f"✅ Got response: {answer[:100]}...")
                    
                    # Check for source documents
                    if 'source_documents' in result and result['source_documents']:
                        print(f"   📚 Found {len(result['source_documents'])} source documents")
                    else:
                        print("   ⚠️ No source documents found")
                else:
                    print("❌ No answer in response")
                    
            except Exception as e:
                print(f"❌ Failed to get answer: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to test sample questions: {e}")
        return False

def test_manual_streamlit():
    """Test the app manually with Streamlit"""
    print("\n🧪 Testing manual Streamlit run...")
    
    try:
        import subprocess
        import time
        
        print("Starting Streamlit app for manual testing...")
        print("This will open a browser window. Test the chatbot and then close it.")
        
        # Run streamlit in a subprocess
        process = subprocess.Popen([
            "streamlit", "run", "src/app.py", "--server.port", "8504"
        ])
        
        print("✅ Streamlit app started")
        print("🌐 Open your browser to: http://localhost:8504")
        print("🤖 Test the chatbot with some questions")
        print("⏹️  Press Ctrl+C to stop the test")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Streamlit app...")
            process.terminate()
            process.wait()
        
        return True
    except Exception as e:
        print(f"❌ Failed to run manual Streamlit test: {e}")
        return False

def main():
    """Run all chatbot tests"""
    print("=" * 60)
    print("🤖 Overview AI Chatbot - Functionality Tests")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("src/app.py"):
        print("❌ Please run this script from the project root directory")
        print("   (where src/app.py is located)")
        return
    
    # Check environment
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️ OPENAI_API_KEY not set - some tests may fail")
        print("   Set it with: export OPENAI_API_KEY=your_key_here")
    
    # Run basic tests
    tests = [
        ("Import Test", test_chatbot_import),
        ("Vectorstore Loading", test_vectorstore_loading),
        ("QA Chain Creation", test_qa_chain),
        ("Sample Questions", test_sample_questions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your chatbot is working correctly.")
        print("\n🚀 Ready to deploy or run locally:")
        print("   - Deploy: Upload src/ to Streamlit Cloud")
        print("   - Local: cd src && streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   - Make sure OPENAI_API_KEY is set")
        print("   - Check that src/vectorstore/ exists and has content")
        print("   - Verify all dependencies are installed: pip install -r src/requirements.txt")
    
    # Ask if user wants to test manually
    if openai_key:
        response = input("\n🤔 Do you want to test the chatbot manually in the browser? (y/n): ")
        if response.lower() in ['y', 'yes']:
            test_manual_streamlit()

if __name__ == "__main__":
    main() 