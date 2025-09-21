#!/bin/bash

# Deploy Agents to Google Cloud Agent Engine using Agent Starter Pack (ASP)
# Based on: https://google.github.io/adk-docs/deploy/agent-engine/#deploy-to-agent-engine

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
REGION="us-central1"

echo "🚀 Deploying Agents to Google Cloud Agent Engine using ASP"
echo "=========================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""
echo "📋 Agent Flow Sequence:"
echo "1. Extractor Agent (Entry Point)"
echo "2. Risk Assessment Agent"
echo "3. Meeting Scheduler Agent"
echo "4. ADK Interview Agent (after meeting approved)"
echo "5. Voice Interview Agent (OPTIONAL)"
echo "6. Audio Interview Agent"
echo "7. Memo Generation Agent"
echo "8. Final Evaluation Agent"
echo "9. Main Orchestrator"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV tool is not installed. Please install it first."
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if make is installed
if ! command -v make &> /dev/null; then
    echo "❌ Make tool is not installed. Please install it first."
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install it first."
    exit 1
fi

echo "✅ All prerequisites are installed"

# Set the project
echo "📋 Setting project..."
gcloud config set project ${PROJECT_ID}

# Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login
gcloud auth application-default login

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Function to deploy a single agent using ASP
deploy_agent_with_asp() {
    local agent_name=$1
    local agent_file=$2
    local agent_id=$3
    
    echo ""
    echo "🤖 Deploying ${agent_name} to Agent Engine..."
    echo "============================================="
    
    # Create a temporary directory for the agent
    local agent_dir="temp_agents/${agent_name}"
    mkdir -p "${agent_dir}"
    
    # Copy the agent file to the temp directory
    if [ -f "backend/agents/${agent_file}" ]; then
        cp "backend/agents/${agent_file}" "${agent_dir}/"
        
        # Create a simple main.py for the agent
        cat > "${agent_dir}/main.py" << EOF
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the agent
from ${agent_file%.py} import *

# This will be enhanced by ASP
if __name__ == "__main__":
    pass
EOF
        
        # Create pyproject.toml for the agent
        cat > "${agent_dir}/pyproject.toml" << EOF
[project]
name = "${agent_name}"
version = "1.0.0"
description = "AI agent for startup evaluation"
requires-python = ">=3.9"
dependencies = [
    "google-adk>=0.2.0",
    "fastapi>=0.115.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.5.0",
    "google-cloud-storage>=2.10.0",
    "google-cloud-aiplatform>=1.71.1",
    "vertexai>=1.71.1",
    "python-dotenv>=1.0.0",
    "sqlalchemy>=2.0.23",
    "pg8000>=1.30.3",
    "psycopg2-binary>=2.9.9"
]
EOF
        
        # Navigate to the agent directory
        cd "${agent_dir}"
        
        # Use ASP to enhance the project for Agent Engine deployment
        echo "   📦 Preparing agent with ASP..."
        uvx agent-starter-pack enhance --adk -d agent_engine --region ${REGION} --auto-approve
        
        # Install dependencies and deploy using make commands
        echo "   📦 Installing dependencies..."
        make install
        
        # Deploy the agent to Agent Engine
        echo "   🚀 Deploying to Agent Engine..."
        make deploy
        
        # Navigate back
        cd - > /dev/null
        
        echo "   ✅ ${agent_name} deployed to Agent Engine"
    else
        echo "   ⚠️  Agent file ${agent_file} not found, skipping ${agent_name}"
    fi
}

# Create temp directory
mkdir -p temp_agents

# Define agents in correct flow order
agents=(
    "extractor_agent:extractor_agent.py:extractor-agent"
    "risk_agent:risk_agent.py:risk-assessment-agent"
    "meeting_scheduler_agent:meeting_scheduler_agent.py:meeting-scheduler-agent"
    "adk_interview_agent:adk_interview_agent.py:adk-interview-agent"
    "voice_interview_agent:voice_interview_agent.py:voice-interview-agent"
    "audio_interview_agent:audio_interview_agent.py:audio-interview-agent"
    "memo_agent:memo_agent.py:memo-generation-agent"
    "final_evaluation_agent:final_evaluation_agent.py:final-evaluation-agent"
    "orchestrator:orchestrator.py:main-orchestrator"
)

# Deploy each agent in correct order
for agent_info in "${agents[@]}"; do
    IFS=':' read -r agent_name agent_file agent_id <<< "${agent_info}"
    deploy_agent_with_asp "${agent_name}" "${agent_file}" "${agent_id}"
done

echo ""
echo "🎉 All Agents Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Deployed Agents (in Agent Engine):"
echo "  ✅ 1. Extractor Agent (Entry Point)"
echo "  ✅ 2. Risk Assessment Agent"
echo "  ✅ 3. Meeting Scheduler Agent"
echo "  ✅ 4. ADK Interview Agent"
echo "  ✅ 5. Voice Interview Agent (OPTIONAL)"
echo "  ✅ 6. Audio Interview Agent"
echo "  ✅ 7. Memo Generation Agent"
echo "  ✅ 8. Final Evaluation Agent"
echo "  ✅ 9. Main Orchestrator"
echo ""
echo "🔄 Agent Flow:"
echo "   Extractor → Risk → Meeting Scheduler →"
echo "   ADK Interview (after meeting approved) → Memo →"
echo "   Final Evaluation → Main Orchestrator"
echo ""
echo "📝 Key Points:"
echo "   • Risk Assessment → Meeting Scheduler → Interview Agent"
echo "   • Interview Agent starts only after meeting is approved"
echo "   • Voice Interview is OPTIONAL"
echo "   • All agents deployed to Agent Engine using ASP"
echo ""
echo "🔗 Access your agents in Google Cloud Console:"
echo "   https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=${PROJECT_ID}"
echo ""
echo "📝 Next steps:"
echo "1. Test the complete agent flow starting with document upload"
echo "2. Verify agent communication and data flow"
echo "3. Monitor agent performance in Cloud Console"
echo "4. Configure agent triggers and workflows"

# Clean up temporary files
rm -rf temp_agents

echo ""
echo "✨ All agents are now deployed to Agent Engine using ASP!"