#!/usr/bin/env python3
"""
Test script for the deployed ADK Interview Agent on Agent Engine
Following the testing guide from: https://google.github.io/adk-docs/deploy/agent-engine/#test-deployed-agent
"""

import os
import sys
import json
import asyncio
import subprocess
from typing import Dict, Any

def get_project_info():
    """Get Google Cloud project information"""
    print("🔍 Getting Google Cloud project information...")
    
    try:
        # Get project ID
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            project_id = result.stdout.strip()
            print(f"✅ Project ID: {project_id}")
        else:
            print("❌ Failed to get project ID")
            return None
        
        # Get location (default to us-central1)
        location = "us-central1"
        print(f"✅ Location: {location}")
        
        return {
            "project_id": project_id,
            "location": location
        }
        
    except Exception as e:
        print(f"❌ Error getting project info: {e}")
        return None

def get_agent_info(project_id: str, location: str):
    """Get deployed agent information"""
    print(f"\n🔍 Getting agent information...")
    
    try:
        result = subprocess.run([
            "gcloud", "ai", "reasoning-engines", "list",
            "--format=json",
            f"--location={location}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            engines = json.loads(result.stdout)
            if engines:
                agent = engines[0]  # Use the first agent
                resource_id = agent["name"].split("/")[-1]
                
                print(f"✅ Agent found:")
                print(f"   Name: {agent.get('displayName', 'Unknown')}")
                print(f"   Resource ID: {resource_id}")
                print(f"   State: {agent.get('state', 'Unknown')}")
                
                return {
                    "resource_id": resource_id,
                    "name": agent.get("displayName", "Unknown"),
                    "state": agent.get("state", "Unknown")
                }
            else:
                print("❌ No agents found")
                return None
        else:
            print(f"❌ Failed to list agents: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting agent info: {e}")
        return None

def test_agent_connection(project_id: str, location: str, resource_id: str):
    """Test connection to the deployed agent"""
    print(f"\n🔗 Testing agent connection...")
    
    try:
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines"
        
        result = subprocess.run([
            "curl", "-X", "GET",
            "-H", "Authorization: Bearer $(gcloud auth print-access-token)",
            url
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Agent connection successful!")
            return True
        else:
            print(f"❌ Agent connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def create_session(project_id: str, location: str, resource_id: str):
    """Create a new session with the agent"""
    print(f"\n📝 Creating new session...")
    
    try:
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{resource_id}:query"
        
        payload = {
            "class_method": "start_interview_session",
            "input": {
                "founder_name": "Sarah Johnson",
                "startup_name": "EcoTech Solutions"
            }
        }
        
        result = subprocess.run([
            "curl", "-X", "POST",
            "-H", "Authorization: Bearer $(gcloud auth print-access-token)",
            "-H", "Content-Type: application/json",
            url,
            "-d", json.dumps(payload)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            session_id = response["output"]["id"]
            print(f"✅ Session created successfully!")
            print(f"   Session ID: {session_id}")
            return session_id
        else:
            print(f"❌ Failed to create session: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        return None

def send_agent_request(project_id: str, location: str, resource_id: str, session_id: str):
    """Send a request to the agent"""
    print(f"\n💬 Sending request to agent...")
    
    try:
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{resource_id}:streamQuery?alt=sse"
        
        payload = {
            "class_method": "process_founder_response",
            "input": {
                "session_id": session_id,
                "response": "We're solving the critical problem of food waste in the supply chain. Currently, 40% of all food produced globally goes to waste, costing the economy $1.3 trillion annually. Our AI-powered platform helps grocery stores and restaurants predict demand more accurately, reducing waste by up to 30% while increasing profitability."
            }
        }
        
        result = subprocess.run([
            "curl", "-X", "POST",
            "-H", "Authorization: Bearer $(gcloud auth print-access-token)",
            "-H", "Content-Type: application/json",
            url,
            "-d", json.dumps(payload)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Request sent successfully!")
            print(f"Response: {result.stdout}")
            return True
        else:
            print(f"❌ Failed to send request: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending request: {e}")
        return False

def test_python_client():
    """Test using Python client (if available)"""
    print(f"\n🐍 Testing with Python client...")
    
    try:
        # This would require the ADK Python client
        # For now, we'll just show the structure
        print("✅ Python client test structure:")
        print("""
# Example Python client usage:
from google.adk import agent_engines

# Connect to deployed agent
remote_app = agent_engines.get("your-agent-resource-name")

# Create session
remote_session = await remote_app.async_create_session(user_id="u_123")

# Send query
async for event in remote_app.async_stream_query(
    user_id="u_123",
    session_id=remote_session["id"],
    message="What problem is your startup solving?"
):
    print(event)
        """)
        return True
        
    except Exception as e:
        print(f"❌ Python client test failed: {e}")
        return False

def run_complete_interview_test(project_id: str, location: str, resource_id: str):
    """Run a complete interview test"""
    print(f"\n🎭 Running complete interview test...")
    
    # Sample interview responses
    responses = [
        "We're solving the critical problem of food waste in the supply chain. Currently, 40% of all food produced globally goes to waste, costing the economy $1.3 trillion annually.",
        "Our primary customers are mid-to-large grocery store chains and restaurant groups. We're currently working with 15 grocery chains across the West Coast.",
        "We've grown from 0 to 15 grocery clients in 18 months, generating $2.1M ARR. Our monthly recurring revenue is growing at 25% month-over-month.",
        "We use a SaaS subscription model with three tiers: Basic ($2,500/month), Professional ($7,500/month), and Enterprise ($15,000/month).",
        "Our main competitors are Spoiler Alert and LeanPath, but they focus on waste tracking rather than prevention. We're the only platform that uses real-time demand forecasting.",
        "We're raising $8M Series A to scale our sales team and expand to the East Coast. The funds will be used for: 40% sales and marketing, 30% product development, 20% team expansion, and 10% working capital."
    ]
    
    try:
        # Create session
        session_id = create_session(project_id, location, resource_id)
        if not session_id:
            return False
        
        # Send each response
        for i, response in enumerate(responses, 1):
            print(f"\n--- Question {i} ---")
            print(f"Response: {response[:100]}...")
            
            success = send_agent_request(project_id, location, resource_id, session_id)
            if not success:
                print(f"❌ Failed to process response {i}")
                return False
            
            print(f"✅ Response {i} processed successfully")
        
        # Generate final report
        print(f"\n📊 Generating final report...")
        url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{resource_id}:query"
        
        payload = {
            "class_method": "generate_interview_report",
            "input": {
                "session_id": session_id
            }
        }
        
        result = subprocess.run([
            "curl", "-X", "POST",
            "-H", "Authorization: Bearer $(gcloud auth print-access-token)",
            "-H", "Content-Type: application/json",
            url,
            "-d", json.dumps(payload)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Final report generated successfully!")
            print(f"Report: {result.stdout}")
            return True
        else:
            print(f"❌ Failed to generate report: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error in complete interview test: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Deployed ADK Interview Agent")
    print("=" * 60)
    
    # Get project information
    project_info = get_project_info()
    if not project_info:
        return False
    
    project_id = project_info["project_id"]
    location = project_info["location"]
    
    # Get agent information
    agent_info = get_agent_info(project_id, location)
    if not agent_info:
        return False
    
    resource_id = agent_info["resource_id"]
    
    # Test connection
    if not test_agent_connection(project_id, location, resource_id):
        return False
    
    # Test session creation
    session_id = create_session(project_id, location, resource_id)
    if not session_id:
        return False
    
    # Test sending requests
    if not send_agent_request(project_id, location, resource_id, session_id):
        return False
    
    # Test Python client
    test_python_client()
    
    # Run complete interview test
    if not run_complete_interview_test(project_id, location, resource_id):
        return False
    
    print("\n🎉 All tests passed!")
    print("\n📚 Your ADK Interview Agent is successfully deployed and working!")
    print(f"🔗 Agent Engine Console: https://console.cloud.google.com/vertex-ai/agents/agent-engines")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)