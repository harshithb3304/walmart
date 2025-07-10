#!/usr/bin/env python3
"""
Troubleshoot import issues for the AI Shopping Assistant
"""

import sys
import subprocess
import importlib.util

def check_import(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        if package_name:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                print(f"❌ {module_name} ({package_name}) - NOT FOUND")
                return False
        
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {module_name} - version {version}")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - OTHER ERROR: {e}")
        return False

def install_package(package_name):
    """Install a package using pip"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    print("🔍 AI Shopping Assistant - Import Troubleshooter")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()
    
    # Required packages
    packages = [
        ('flask', 'Flask==3.0.0'),
        ('flask_cors', 'Flask-CORS==4.0.0'),
        ('requests', 'requests==2.31.0'),
        ('google.generativeai', 'google-generativeai==0.3.0'),
        ('dotenv', 'python-dotenv==1.0.0'),
        ('bs4', 'beautifulsoup4==4.12.0'),
        ('googlesearch', 'googlesearch-python==1.2.3'),
    ]
    
    print("Checking required packages:")
    print("-" * 30)
    
    missing_packages = []
    for module_name, package_name in packages:
        if not check_import(module_name):
            missing_packages.append(package_name)
    
    print()
    
    if missing_packages:
        print("⚠️  Missing packages detected!")
        print("Missing packages:", missing_packages)
        print()
        
        install_choice = input("Would you like to install missing packages? (y/n): ").lower()
        if install_choice == 'y':
            print("\nInstalling missing packages...")
            for package in missing_packages:
                install_package(package)
            
            print("\nRe-checking imports after installation:")
            print("-" * 40)
            for module_name, _ in packages:
                check_import(module_name)
        else:
            print("Skipping installation. Run this script again to install packages.")
    else:
        print("🎉 All required packages are available!")
    
    print()
    print("Checking Gemini AI configuration:")
    print("-" * 35)
    
    try:
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            print("✅ Gemini API key found in environment")
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI configured successfully")
            except Exception as e:
                print(f"❌ Gemini configuration error: {e}")
        else:
            print("⚠️  Gemini API key not found")
            print("   Create a .env file with: GEMINI_API_KEY=your_key_here")
    except Exception as e:
        print(f"❌ Gemini check failed: {e}")
    
    print()
    print("📋 Summary:")
    print("-" * 10)
    if not missing_packages:
        print("✅ All imports should work correctly")
        print("✅ Ready to run the AI Shopping Assistant")
    else:
        print("❌ Some packages are missing")
        print("   Run: pip install -r requirements.txt")
        print("   Or use: fix-imports.bat")

if __name__ == "__main__":
    main() 