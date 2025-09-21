#!/usr/bin/env python3
"""
Test script to verify the frontend integration with the deployed ADK Interview Agent
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_backend_health():
    """Test if the backend API is running"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend API is running")
            return True
        else:
            print(f"❌ Backend API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API is not accessible: {e}")
        return False

def test_agent_health():
    """Test if the agent API is accessible"""
    print("\n🔍 Testing agent API health...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/api/agent/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent API is healthy")
            print(f"   Project ID: {data.get('project_id')}")
            print(f"   Location: {data.get('location')}")
            print(f"   Agent Engine: {data.get('agent_engine')}")
            return True
        else:
            print(f"❌ Agent API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Agent API is not accessible: {e}")
        return False

def test_start_interview():
    """Test starting an interview session"""
    print("\n🔍 Testing interview session start...")
    
    try:
        payload = {
            "founder_name": "Test Founder",
            "startup_name": "Test Startup"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/agent/start-interview",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ Interview session started successfully")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Greeting: {data.get('greeting_message', '')[:100]}...")
                return data.get('session_id')
            else:
                print(f"❌ Failed to start interview: {data.get('error_message')}")
                return None
        else:
            print(f"❌ Start interview returned status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to start interview: {e}")
        return None

def test_process_response(session_id):
    """Test processing a founder response"""
    print("\n🔍 Testing response processing...")
    
    try:
        payload = {
            "session_id": session_id,
            "response": "We're solving food waste in supply chains by connecting restaurants with local food banks."
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/agent/process-response",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ Response processed successfully")
                print(f"   Next message: {data.get('next_message', '')[:100]}...")
                if data.get("analysis"):
                    analysis = data["analysis"]
                    print(f"   Sentiment: {analysis.get('sentiment_score', 0):.2f}")
                    print(f"   Confidence: {analysis.get('confidence_score', 0):.2f}")
                return True
            else:
                print(f"❌ Failed to process response: {data.get('error_message')}")
                return False
        else:
            print(f"❌ Process response returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to process response: {e}")
        return False

def test_frontend_access():
    """Test if the frontend is accessible"""
    print("\n🔍 Testing frontend access...")
    
    try:
        response = requests.get("http://127.0.0.1:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend is not accessible: {e}")
        print("   Make sure to run: cd frontend && npm start")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Frontend Integration with ADK Interview Agent")
    print("=" * 60)
    
    # Test backend health
    backend_healthy = test_backend_health()
    if not backend_healthy:
        print("\n❌ Backend is not running. Please start it with:")
        print("   cd backend && uvicorn main:app --reload --port 8000")
        return False
    
    # Test agent health
    agent_healthy = test_agent_health()
    if not agent_healthy:
        print("\n❌ Agent API is not working. Check Agent Engine deployment.")
        return False
    
    # Test interview flow
    session_id = test_start_interview()
    if session_id:
        test_process_response(session_id)
    
    # Test frontend
    frontend_healthy = test_frontend_access()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Backend API: {'✅' if backend_healthy else '❌'}")
    print(f"   Agent API: {'✅' if agent_healthy else '❌'}")
    print(f"   Interview Flow: {'✅' if session_id else '❌'}")
    print(f"   Frontend: {'✅' if frontend_healthy else '❌'}")
    
    if backend_healthy and agent_healthy and frontend_healthy:
        print("\n🎉 All systems are ready!")
        print("\n📝 Next steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Click on 'AI Interview' in the navigation")
        print("   3. Start a conversation with the AI Interview Agent")
        return True
    else:
        print("\n⚠️  Some systems need attention. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)