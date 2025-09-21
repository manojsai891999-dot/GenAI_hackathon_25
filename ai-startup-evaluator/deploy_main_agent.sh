#!/bin/bash

# Deploy Main ADK Interview Agent to Agent Engine using ASP
# This script deploys the main interview agent using the proper ASP method

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
REGION="us-central1"

echo "🚀 Deploying Main ADK Interview Agent to Agent Engine"
echo "===================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
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

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Create a clean agent directory
echo "📦 Preparing main interview agent..."
mkdir -p main_agent_deployment
cd main_agent_deployment

# Create the main agent file
cat > agent.py << 'EOF'
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents import Agent
from google.adk.core import BaseAgent

logger = logging.getLogger(__name__)

class ADKInterviewAgent(BaseAgent):
    """ADK Interview Agent for Startup Founder Evaluation"""
    
    def __init__(self):
        super().__init__()
        self.name = "adk-interview-agent"
        self.description = "AI Interview Agent for Startup Founder Evaluation with CloudSQL + GCS Integration"
        
        # Interview questions
        self.questions = [
            "What problem is your startup solving?",
            "Who are your target customers?",
            "What is your current traction (users, revenue, growth)?",
            "What is your business model?",
            "Who are your competitors and how are you different?",
            "What is your fundraising goal and how will you use the capital?"
        ]
        
        self.current_question_index = 0
        self.responses = []
        self.founder_name = None
        self.session_id = None
    
    async def start_interview(self, founder_name: str, session_id: str) -> str:
        """Start a new interview session"""
        self.founder_name = founder_name
        self.session_id = session_id
        self.current_question_index = 0
        self.responses = []
        
        greeting = f"Hello {founder_name}! Welcome to the startup evaluation interview. "
        greeting += "I'll be asking you a series of questions to better understand your startup. "
        greeting += "Let's begin with the first question."
        
        return greeting
    
    async def get_next_question(self) -> str:
        """Get the next question in the interview"""
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            return f"Question {self.current_question_index + 1}: {question}"
        else:
            return "Thank you! We've completed all the interview questions. I'll now generate a summary report."
    
    async def process_response(self, response: str) -> str:
        """Process the founder's response"""
        if self.current_question_index < len(self.questions):
            # Store the response
            self.responses.append({
                "question": self.questions[self.current_question_index],
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            self.current_question_index += 1
            
            if self.current_question_index < len(self.questions):
                return await self.get_next_question()
            else:
                # Interview complete, generate summary
                return await self.generate_summary()
        else:
            return "The interview is already complete. Thank you!"
    
    async def generate_summary(self) -> str:
        """Generate a summary of the interview"""
        summary = f"Interview Summary for {self.founder_name}\n\n"
        summary += "Key Responses:\n"
        
        for i, response in enumerate(self.responses, 1):
            summary += f"\n{i}. {response['question']}\n"
            summary += f"   Response: {response['response']}\n"
        
        summary += "\n\nThis concludes the interview. Thank you for your time!"
        return summary

# Create the agent instance
adk_interview_agent = ADKInterviewAgent()

if __name__ == "__main__":
    # This will be used by the ADK framework
    pass
EOF

# Create pyproject.toml with compatible versions
cat > pyproject.toml << 'EOF'
[project]
name = "adk-interview-agent"
version = "1.0.0"
description = "AI Interview Agent for Startup Founder Evaluation"
requires-python = ">=3.9"
dependencies = [
    "google-adk>=1.14.0",
    "google-cloud-aiplatform[agent-engines]>=1.115.0",
    "google-cloud-storage>=2.10.0",
    "python-dotenv>=1.0.0",
    "sqlalchemy>=2.0.23",
    "pg8000>=1.30.3",
    "psycopg2-binary>=2.9.9"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF

# Use ASP to enhance the project for Agent Engine deployment
echo "📦 Preparing agent with ASP..."
uvx agent-starter-pack enhance --adk -d agent_engine --region ${REGION} --auto-approve

# Install dependencies
echo "📦 Installing dependencies..."
make install

# Deploy the agent to Agent Engine
echo "🚀 Deploying to Agent Engine..."
make deploy

cd ..

echo ""
echo "🎉 Main ADK Interview Agent Deployment Complete!"
echo "==============================================="
echo ""
echo "✅ ADK Interview Agent deployed to Agent Engine"
echo ""
echo "🔗 Access your agent in Google Cloud Console:"
echo "   https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=${PROJECT_ID}"
echo ""
echo "📝 Next steps:"
echo "1. Test the agent through the frontend chatbot"
echo "2. Monitor agent performance in Cloud Console"
echo "3. Configure agent triggers and workflows"

# Clean up
rm -rf main_agent_deployment

echo ""
echo "✨ Main ADK Interview Agent is now deployed to Agent Engine!"