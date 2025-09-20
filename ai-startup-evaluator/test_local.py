#!/usr/bin/env python3
"""
Test script for AI Startup Evaluator local setup
This script verifies that all components are working correctly
"""

import requests
import time
import sys
from pathlib import Path

def test_backend():
    """Test backend API endpoints"""
    print("🔧 Testing Backend API...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test stats endpoint
        response = requests.get("http://localhost:8000/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working - {data.get('data', {}).get('total_startups', 0)} startups")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
        
        # Test startups list endpoint
        response = requests.get("http://localhost:8000/api/startups", timeout=5)
        if response.status_code == 200:
            startups = response.json()
            print(f"✅ Startups endpoint working - {len(startups)} startups found")
            
            # Test individual startup if available
            if startups:
                startup_id = startups[0]['id']
                response = requests.get(f"http://localhost:8000/api/startup/{startup_id}", timeout=5)
                if response.status_code == 200:
                    startup = response.json()
                    print(f"✅ Individual startup endpoint working - {startup.get('name', 'Unknown')}")
                else:
                    print(f"❌ Individual startup endpoint failed: {response.status_code}")
        else:
            print(f"❌ Startups endpoint failed: {response.status_code}")
            return False
        
        # Test interview questions endpoint
        response = requests.get("http://localhost:8000/api/interview/questions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            questions_data = data.get('data', {})
            total_questions = questions_data.get('total_questions', 0)
            total_categories = questions_data.get('total_categories', 0)
            print(f"✅ Interview questions endpoint working - {total_questions} questions in {total_categories} categories")
        else:
            print(f"❌ Interview questions endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def test_frontend():
    """Test frontend availability"""
    print("\n🎨 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to frontend. Is it running on port 3000?")
        return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("\n💾 Testing Database...")
    
    try:
        db_path = Path("backend/startup_evaluator.db")
        if db_path.exists():
            print(f"✅ SQLite database exists: {db_path}")
            print(f"   Size: {db_path.stat().st_size} bytes")
            return True
        else:
            print("❌ SQLite database not found")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_google_ai_config():
    """Test Google AI API configuration"""
    print("\n🤖 Testing Google AI Configuration...")
    
    try:
        env_path = Path("backend/.env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
                if "GOOGLE_AI_API_KEY=" in content and not content.count("GOOGLE_AI_API_KEY=#") == content.count("GOOGLE_AI_API_KEY="):
                    # Check if there's a non-commented API key
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith("GOOGLE_AI_API_KEY=") and not line.startswith("# GOOGLE_AI_API_KEY="):
                            if len(line.split('=', 1)[1].strip()) > 10:  # Basic check for key length
                                print("✅ Google AI API key is configured")
                                return True
                    print("⚠️  Google AI API key is not configured (AI features will be limited)")
                    print("   Get a key from: https://aistudio.google.com/")
                    return False
                else:
                    print("⚠️  Google AI API key is not configured (AI features will be limited)")
                    return False
        else:
            print("❌ .env file not found")
            return False
    except Exception as e:
        print(f"❌ Google AI config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Startup Evaluator - Local Environment Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the ai-startup-evaluator directory")
        sys.exit(1)
    
    tests_passed = 0
    total_tests = 4
    
    # Test database
    if test_database():
        tests_passed += 1
    
    # Test Google AI config
    if test_google_ai_config():
        tests_passed += 1
    
    # Test backend (requires it to be running)
    if test_backend():
        tests_passed += 1
    
    # Test frontend (requires it to be running)
    if test_frontend():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your local environment is ready.")
        print("\n📋 What you can do now:")
        print("   • Visit http://localhost:3000 to use the app")
        print("   • Check out the sample startup 'TechCorp AI'")
        print("   • View the 32+ predefined interview questions")
        print("   • Try uploading a PDF pitch deck")
        print("   • Explore the API docs at http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n🔧 Common fixes:")
        print("   • Make sure both backend and frontend are running")
        print("   • Run: ./start_local.sh")
        print("   • Configure Google AI API key in backend/.env")
        print("   • Check that ports 3000 and 8000 are available")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
