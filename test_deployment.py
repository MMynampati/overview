#!/usr/bin/env python3
"""
Test the deployment setup (src/ directory)
"""

import os
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

def create_test_deployment():
    """Create a test deployment directory"""
    print("🧪 Creating test deployment...")
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="overview_test_")
    print(f"✅ Created test directory: {temp_dir}")
    
    # Copy src contents to temp directory
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src/ directory not found")
        return None
    
    try:
        # Copy all files from src to temp directory
        for item in src_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, Path(temp_dir) / item.name)
            elif item.is_dir():
                shutil.copytree(item, Path(temp_dir) / item.name)
        
        print("✅ Copied src/ contents to test directory")
        return temp_dir
    except Exception as e:
        print(f"❌ Failed to copy files: {e}")
        return None

def test_deployment_structure(temp_dir):
    """Test if the deployment has all required files"""
    print("\n🧪 Testing deployment structure...")
    
    required_files = [
        "app.py",
        "requirements.txt",
        "README.md"
    ]
    
    required_dirs = [
        "vectorstore"
    ]
    
    passed = 0
    total = len(required_files) + len(required_dirs)
    
    # Check files
    for file in required_files:
        if os.path.exists(os.path.join(temp_dir, file)):
            print(f"✅ {file}")
            passed += 1
        else:
            print(f"❌ {file} (missing)")
    
    # Check directories
    for dir_name in required_dirs:
        if os.path.exists(os.path.join(temp_dir, dir_name)):
            print(f"✅ {dir_name}/")
            passed += 1
        else:
            print(f"❌ {dir_name}/ (missing)")
    
    print(f"\n📊 Structure test: {passed}/{total} items found")
    return passed == total

def test_requirements_install(temp_dir):
    """Test if requirements can be installed"""
    print("\n🧪 Testing requirements installation...")
    
    try:
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Create a virtual environment
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Created virtual environment")
        
        # Install requirements
        if os.name == 'nt':  # Windows
            pip_cmd = os.path.join("venv", "Scripts", "pip")
        else:  # Unix/Linux/Mac
            pip_cmd = os.path.join("venv", "bin", "pip")
        
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Installed requirements")
        
        os.chdir(original_dir)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        os.chdir(original_dir)
        return False
    except Exception as e:
        print(f"❌ Error during installation test: {e}")
        os.chdir(original_dir)
        return False

def test_app_import(temp_dir):
    """Test if the app can be imported in the deployment environment"""
    print("\n🧪 Testing app import in deployment environment...")
    
    try:
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Activate virtual environment and test import
        if os.name == 'nt':  # Windows
            python_cmd = os.path.join("venv", "Scripts", "python")
        else:  # Unix/Linux/Mac
            python_cmd = os.path.join("venv", "bin", "python")
        
        # Test import
        result = subprocess.run([
            python_cmd, "-c", "import app; print('✅ App imported successfully')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            os.chdir(original_dir)
            return True
        else:
            print(f"❌ Import failed: {result.stderr}")
            os.chdir(original_dir)
            return False
    except Exception as e:
        print(f"❌ Error during import test: {e}")
        os.chdir(original_dir)
        return False

def test_streamlit_run(temp_dir):
    """Test if Streamlit can run the app"""
    print("\n🧪 Testing Streamlit run...")
    
    try:
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Activate virtual environment and test streamlit
        if os.name == 'nt':  # Windows
            streamlit_cmd = os.path.join("venv", "Scripts", "streamlit")
        else:  # Unix/Linux/Mac
            streamlit_cmd = os.path.join("venv", "bin", "streamlit")
        
        # Test streamlit run (with headless mode)
        process = subprocess.Popen([
            streamlit_cmd, "run", "app.py", "--server.headless", "true", "--server.port", "8503"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for it to start
        import time
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Streamlit app started successfully")
            process.terminate()
            process.wait()
            os.chdir(original_dir)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit failed to start: {stderr.decode()}")
            os.chdir(original_dir)
            return False
    except Exception as e:
        print(f"❌ Error during Streamlit test: {e}")
        os.chdir(original_dir)
        return False

def cleanup_test_deployment(temp_dir):
    """Clean up the test deployment"""
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            print(f"✅ Cleaned up test directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️ Failed to clean up test directory: {e}")

def main():
    """Run deployment tests"""
    print("=" * 60)
    print("🚀 Overview AI Chatbot - Deployment Tests")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("src/app.py"):
        print("❌ Please run this script from the project root directory")
        print("   (where src/app.py is located)")
        return
    
    temp_dir = None
    try:
        # Create test deployment
        temp_dir = create_test_deployment()
        if not temp_dir:
            return
        
        # Run tests
        tests = [
            ("Structure Test", lambda: test_deployment_structure(temp_dir)),
            ("Requirements Install", lambda: test_requirements_install(temp_dir)),
            ("App Import", lambda: test_app_import(temp_dir)),
            ("Streamlit Run", lambda: test_streamlit_run(temp_dir))
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
        print(f"📊 Deployment Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All deployment tests passed!")
            print("✅ Your src/ directory is ready for deployment")
            print("\n🚀 Next steps:")
            print("   - Upload src/ to Streamlit Cloud")
            print("   - Set OPENAI_API_KEY in Streamlit Cloud secrets")
            print("   - Deploy!")
        else:
            print("⚠️ Some deployment tests failed.")
            print("🔧 Check the errors above and fix them before deploying.")
    
    finally:
        # Clean up
        cleanup_test_deployment(temp_dir)

if __name__ == "__main__":
    main() 