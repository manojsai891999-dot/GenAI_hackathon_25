#!/usr/bin/env python3
"""
Deployment script for ADK Interview Agent to Google Cloud Agent Engine
Following the official ADK deployment guide: https://google.github.io/adk-docs/deploy/agent-engine/
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print("🔍 Checking prerequisites...")
    
    prerequisites = {
        "python": "python3 --version",
        "gcloud": "gcloud --version",
        "uv": "uv --version",
        "make": "make --version",
        "terraform": "terraform --version"
    }
    
    missing = []
    
    for tool, command in prerequisites.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool}: {result.stdout.strip().split()[0]}")
            else:
                missing.append(tool)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing prerequisites: {', '.join(missing)}")
        print("\nPlease install the missing tools:")
        for tool in missing:
            if tool == "uv":
                print("  - UV: https://docs.astral.sh/uv/getting-started/installation/")
            elif tool == "gcloud":
                print("  - Google Cloud CLI: https://cloud.google.com/sdk/docs/install")
            elif tool == "terraform":
                print("  - Terraform: https://developer.hashicorp.com/terraform/downloads")
        return False
    
    print("✅ All prerequisites are installed!")
    return True

def prepare_project():
    """Prepare the ADK project for deployment using Agent Starter Pack"""
    print("\n📦 Preparing project for deployment...")
    
    try:
        # Run the ASP enhance command
        cmd = [
            "uvx", "agent-starter-pack", "enhance", 
            "--adk", "-d", "agent_engine"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=".", capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Project prepared successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Project preparation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error preparing project: {e}")
        return False

def authenticate_gcloud():
    """Authenticate with Google Cloud"""
    print("\n🔐 Authenticating with Google Cloud...")
    
    try:
        # Check if already authenticated
        result = subprocess.run(["gcloud", "auth", "list"], capture_output=True, text=True)
        if "ACTIVE" in result.stdout:
            print("✅ Already authenticated with Google Cloud")
            return True
        
        # Authenticate
        result = subprocess.run(["gcloud", "auth", "login"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Successfully authenticated with Google Cloud")
            return True
        else:
            print(f"❌ Authentication failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

def set_project(project_id):
    """Set the Google Cloud project"""
    print(f"\n🎯 Setting Google Cloud project to {project_id}...")
    
    try:
        result = subprocess.run(
            ["gcloud", "config", "set", "project", project_id],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Project set to {project_id}")
            return True
        else:
            print(f"❌ Failed to set project: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting project: {e}")
        return False

def deploy_agent():
    """Deploy the agent to Agent Engine"""
    print("\n🚀 Deploying agent to Agent Engine...")
    
    try:
        # Check if Makefile exists (created by ASP)
        if not Path("Makefile").exists():
            print("❌ Makefile not found. Please run project preparation first.")
            return False
        
        # Run deployment
        result = subprocess.run(["make", "deploy"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Agent deployed successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False

def get_deployment_info():
    """Get information about the deployed agent"""
    print("\n📊 Getting deployment information...")
    
    try:
        # List reasoning engines
        result = subprocess.run(
            ["gcloud", "ai", "reasoning-engines", "list", "--format=json"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            engines = json.loads(result.stdout)
            if engines:
                print("✅ Deployed agents:")
                for engine in engines:
                    print(f"  - Name: {engine.get('name', 'Unknown')}")
                    print(f"    Display Name: {engine.get('displayName', 'Unknown')}")
                    print(f"    State: {engine.get('state', 'Unknown')}")
                    print(f"    Create Time: {engine.get('createTime', 'Unknown')}")
                    print()
                return engines
            else:
                print("⚠️  No agents found")
                return []
        else:
            print(f"❌ Failed to list agents: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting deployment info: {e}")
        return []

def test_deployed_agent(project_id, location="us-central1"):
    """Test the deployed agent"""
    print(f"\n🧪 Testing deployed agent...")
    
    try:
        # Get the agent resource name
        engines = get_deployment_info()
        if not engines:
            print("❌ No agents found to test")
            return False
        
        # Use the first agent
        agent_name = engines[0]["name"]
        resource_id = agent_name.split("/")[-1]
        
        print(f"Testing agent: {agent_name}")
        
        # Test with a simple request
        test_payload = {
            "class_method": "start_interview_session",
            "input": {
                "founder_name": "Test Founder",
                "startup_name": "Test Startup"
            }
        }
        
        # Create a session
        session_cmd = [
            "curl", "-X", "POST",
            "-H", "Authorization: Bearer $(gcloud auth print-access-token)",
            "-H", "Content-Type: application/json",
            f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{resource_id}:query",
            "-d", json.dumps(test_payload)
        ]
        
        print("Testing agent functionality...")
        result = subprocess.run(session_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Agent test successful!")
            print(f"Response: {result.stdout}")
            return True
        else:
            print(f"❌ Agent test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 ADK Interview Agent Deployment to Agent Engine")
    print("=" * 60)
    
    # Get project ID from user
    project_id = input("Enter your Google Cloud Project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return False
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    # Prepare project
    if not prepare_project():
        return False
    
    # Authenticate with Google Cloud
    if not authenticate_gcloud():
        return False
    
    # Set project
    if not set_project(project_id):
        return False
    
    # Deploy agent
    if not deploy_agent():
        return False
    
    # Get deployment info
    get_deployment_info()
    
    # Test deployed agent
    test_deployed_agent(project_id)
    
    print("\n🎉 Deployment completed!")
    print("\n📚 Next steps:")
    print("1. Check the Agent Engine console: https://console.cloud.google.com/vertex-ai/agents/agent-engines")
    print("2. Test your agent using the REST API or Python client")
    print("3. Monitor usage and performance in the Google Cloud Console")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)