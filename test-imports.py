#!/usr/bin/env python3
"""
Quick test to see what imports are working
"""

print("🔍 Testing imports...")
print("-" * 30)

# Test basic imports
try:
    import flask
    print("✅ Flask:", flask.__version__)
except ImportError as e:
    print("❌ Flask:", e)

try:
    import flask_cors
    print("✅ Flask-CORS: Available")
except ImportError as e:
    print("❌ Flask-CORS:", e)

try:
    import requests
    print("✅ Requests:", requests.__version__)
except ImportError as e:
    print("❌ Requests:", e)

# Test AI imports
try:
    import google.generativeai as genai
    print("✅ Google GenerativeAI: Available")
except ImportError as e:
    print("❌ Google GenerativeAI:", e)

try:
    from dotenv import load_dotenv
    print("✅ Python-dotenv: Available")
except ImportError as e:
    print("❌ Python-dotenv:", e)

# Test web scraping imports
try:
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup: Available")
except ImportError as e:
    print("❌ BeautifulSoup:", e)

try:
    from googlesearch import search
    print("✅ GoogleSearch: Available")
except ImportError as e:
    print("❌ GoogleSearch:", e)

print("\n" + "=" * 40)
print("RECOMMENDATION:")
print("=" * 40)

# Count working imports
working_basic = 0
try:
    import flask, flask_cors, requests
    working_basic = 3
except:
    pass

if working_basic == 3:
    print("✅ Basic Flask setup is working!")
    print("✅ You can run: start-simple.bat")
    print("✅ This will work even without AI dependencies")
else:
    print("❌ Basic Flask setup needs fixing")
    print("🔧 Run: fix-imports.bat")
    print("🔧 Or install manually: pip install Flask Flask-CORS requests")

print("\nFor full AI features, you'll also need:")
print("- google-generativeai")
print("- python-dotenv") 
print("- beautifulsoup4")
print("- googlesearch-python") 