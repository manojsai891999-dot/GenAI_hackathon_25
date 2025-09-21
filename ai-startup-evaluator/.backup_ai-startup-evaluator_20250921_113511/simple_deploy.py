#!/usr/bin/env python3
"""
Simplified deployment script for ADK Interview Agent
This version focuses on preparing the agent for deployment without requiring all prerequisites
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_basic_prerequisites():
    """Check basic prerequisites for deployment"""
    print("🔍 Checking basic prerequisites...")
    
    prerequisites = {
        "python": "python3 --version",
        "gcloud": "gcloud --version"
    }
    
    missing = []
    
    for tool, command in prerequisites.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool}: Available")
            else:
                missing.append(tool)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing prerequisites: {', '.join(missing)}")
        return False
    
    print("✅ Basic prerequisites are available!")
    return True

def prepare_agent_files():
    """Prepare the agent files for deployment"""
    print("\n📦 Preparing agent files for deployment...")
    
    # Ensure all required files exist
    required_files = [
        "main_agent.py",
        "agent_config.yaml",
        "requirements.txt",
        "backend/agents/adk_interview_agent.py",
        "backend/models/database.py",
        "backend/models/schemas.py",
        "backend/services/gcs_service.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files are present!")
    return True

def create_deployment_manifest():
    """Create a deployment manifest for the agent"""
    print("\n📋 Creating deployment manifest...")
    
    manifest = {
        "name": "adk-interview-agent",
        "version": "1.0.0",
        "description": "AI Interview Agent for Startup Founder Evaluation with CloudSQL + GCS Integration",
        "runtime": "python3.11",
        "entrypoint": "main_agent.py",
        "requirements": "requirements.txt",
        "environment": {
            "DATABASE_URL": "postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db",
            "GCS_BUCKET_NAME": "startup-evaluator-storage",
            "DEBUG": "false"
        },
        "resources": {
            "memory": "2Gi",
            "cpu": "2",
            "timeout": "300s"
        },
        "tools": [
            "start_interview_session",
            "process_founder_response",
            "get_interview_status",
            "generate_interview_report",
            "list_active_sessions"
        ]
    }
    
    with open("deployment_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print("✅ Deployment manifest created!")
    return True

def test_agent_locally():
    """Test the agent locally before deployment"""
    print("\n🧪 Testing agent locally...")
    
    try:
        # Set environment variable for local testing
        os.environ["DATABASE_URL"] = "sqlite:///./test_startup_evaluator.db"
        
        # Test importing the main agent
        sys.path.append(".")
        from main_agent import adk_interview_agent
        
        print("✅ Agent imports successfully!")
        
        # Test basic functionality
        print("✅ Agent object created successfully!")
        print(f"   Agent name: {adk_interview_agent.name}")
        print(f"   Agent description: {adk_interview_agent.description}")
        print(f"   Available tools: {len(adk_interview_agent.tools)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        return False

def create_dockerfile():
    """Create a Dockerfile for containerized deployment"""
    print("\n🐳 Creating Dockerfile...")
    
    dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db
ENV GCS_BUCKET_NAME=startup-evaluator-storage
ENV DEBUG=false

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main_agent.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile created!")
    return True

def create_cloud_run_config():
    """Create Cloud Run configuration"""
    print("\n☁️ Creating Cloud Run configuration...")
    
    cloud_run_config = {
        "apiVersion": "serving.knative.dev/v1",
        "kind": "Service",
        "metadata": {
            "name": "adk-interview-agent",
            "annotations": {
                "run.googleapis.com/ingress": "all",
                "run.googleapis.com/execution-environment": "gen2"
            }
        },
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "autoscaling.knative.dev/maxScale": "10",
                        "run.googleapis.com/cpu-throttling": "false",
                        "run.googleapis.com/execution-environment": "gen2"
                    }
                },
                "spec": {
                    "containerConcurrency": 100,
                    "timeoutSeconds": 300,
                    "containers": [{
                        "image": "gcr.io/PROJECT_ID/adk-interview-agent",
                        "ports": [{
                            "containerPort": 8080
                        }],
                        "env": [{
                            "name": "DATABASE_URL",
                            "value": "postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db"
                        }, {
                            "name": "GCS_BUCKET_NAME",
                            "value": "startup-evaluator-storage"
                        }, {
                            "name": "DEBUG",
                            "value": "false"
                        }],
                        "resources": {
                            "limits": {
                                "cpu": "2",
                                "memory": "2Gi"
                            }
                        }
                    }]
                }
            }
        }
    }
    
    with open("cloud-run-config.yaml", "w") as f:
        import yaml
        yaml.dump(cloud_run_config, f, default_flow_style=False)
    
    print("✅ Cloud Run configuration created!")
    return True

def create_deployment_instructions():
    """Create deployment instructions"""
    print("\n📚 Creating deployment instructions...")
    
    instructions = """# ADK Interview Agent - Deployment Instructions

## Prerequisites
- Google Cloud Project with billing enabled
- CloudSQL instance: startup-evaluator-db
- GCS bucket: startup-evaluator-storage
- gcloud CLI installed and authenticated

## Deployment Options

### Option 1: Agent Engine (Recommended)
1. Install Agent Starter Pack: `pip install agent-starter-pack`
2. Run: `uvx agent-starter-pack enhance --adk -d agent_engine`
3. Follow the prompts and deploy

### Option 2: Cloud Run
1. Build container: `gcloud builds submit --tag gcr.io/PROJECT_ID/adk-interview-agent`
2. Deploy: `gcloud run deploy adk-interview-agent --image gcr.io/PROJECT_ID/adk-interview-agent --platform managed --region us-central1`

### Option 3: Manual Agent Engine
1. Create a new agent in the Agent Engine console
2. Upload the main_agent.py file
3. Configure environment variables
4. Deploy

## Testing
Run: `python test_deployed_agent.py`

## Configuration
- Database: startup-evaluator-db/startup_evaluator
- User: app-user
- Password: aianalyst
- GCS Bucket: startup-evaluator-storage
"""
    
    with open("DEPLOYMENT_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Deployment instructions created!")
    return True

def main():
    """Main preparation function"""
    print("🚀 ADK Interview Agent - Deployment Preparation")
    print("=" * 60)
    
    # Check prerequisites
    if not check_basic_prerequisites():
        print("\n❌ Please install missing prerequisites and try again")
        return False
    
    # Prepare agent files
    if not prepare_agent_files():
        print("\n❌ Please ensure all required files are present")
        return False
    
    # Create deployment manifest
    if not create_deployment_manifest():
        print("\n❌ Failed to create deployment manifest")
        return False
    
    # Test agent locally
    if not test_agent_locally():
        print("\n❌ Local test failed, please fix issues before deployment")
        return False
    
    # Create Dockerfile
    create_dockerfile()
    
    # Create Cloud Run config
    create_cloud_run_config()
    
    # Create deployment instructions
    create_deployment_instructions()
    
    print("\n🎉 Agent preparation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the deployment instructions in DEPLOYMENT_INSTRUCTIONS.md")
    print("2. Choose your deployment method (Agent Engine recommended)")
    print("3. Follow the specific deployment steps for your chosen method")
    print("4. Test your deployed agent using test_deployed_agent.py")
    
    print("\n📁 Files created:")
    print("   - deployment_manifest.json")
    print("   - Dockerfile")
    print("   - cloud-run-config.yaml")
    print("   - DEPLOYMENT_INSTRUCTIONS.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)