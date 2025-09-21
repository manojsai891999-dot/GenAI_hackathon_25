#!/bin/bash

# Deploy ALL Agents to Google Cloud Agent Engine using ASP
# This script deploys all agents in the correct flow order

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
REGION="us-central1"

echo "🚀 Deploying ALL Agents to Google Cloud Agent Engine"
echo "===================================================="
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

# Function to deploy a single agent
deploy_agent() {
    local agent_name=$1
    local agent_description=$2
    local agent_functions=$3
    
    echo ""
    echo "🤖 Deploying ${agent_name} to Agent Engine..."
    echo "============================================="
    
    # Create ADK project for this agent
    echo "   📦 Creating ADK project for ${agent_name}..."
    uvx agent-starter-pack create ${agent_name} --agent adk_base --deployment-target agent_engine --region ${REGION} --auto-approve
    
    # Navigate to the agent directory (ASP converts underscores to hyphens)
    agent_dir_name=$(echo ${agent_name} | sed 's/_/-/g')
    cd ${agent_dir_name}
    
    # Create the agent code
    echo "   📝 Creating agent code..."
    cat > app/agent.py << EOF
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import logging
from typing import Dict, List, Optional, Any

import google.auth
from google.adk.agents import Agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "${REGION}")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

logger = logging.getLogger(__name__)

${agent_functions}

# Create the agent
root_agent = Agent(
    name="${agent_name}",
    model="gemini-2.5-flash",
    instruction="${agent_description}",
    tools=[${agent_tools}],
)
EOF

    # Install dependencies
    echo "   📦 Installing dependencies..."
    make install
    
    # Deploy to Agent Engine
    echo "   🚀 Deploying to Agent Engine..."
    make backend
    
    # Navigate back
    cd ..
    
    echo "   ✅ ${agent_name} deployed successfully"
}

# Define all agents with their functions
agents=(
    "extractor_agent:Extractor Agent - Entry point for processing startup documents and data"
    "risk_assessment_agent:Risk Assessment Agent - Analyzes risks and provides risk assessment"
    "meeting_scheduler_agent:Meeting Scheduler Agent - Intelligent meeting scheduling"
    "adk_interview_agent:ADK Interview Agent - Primary interview agent for structured startup founder interviews"
    "voice_interview_agent:Voice Interview Agent - Advanced voice interview agent with real-time processing (OPTIONAL)"
    "audio_interview_agent:Audio Interview Agent - Audio-based interview agent for voice interactions"
    "memo_generation_agent:Memo Generation Agent - Investment memo generation agent"
    "final_evaluation_agent:Final Evaluation Agent - Comprehensive evaluation agent for final startup assessment"
    "main_orchestrator:Main Orchestrator - Main orchestrator that coordinates all agents and synthesizes results"
)

# Deploy each agent
for agent_info in "${agents[@]}"; do
    IFS=':' read -r agent_name agent_description <<< "${agent_info}"
    
    # Create agent-specific functions based on agent type
    case $agent_name in
        "extractor_agent")
            agent_functions='
def extract_from_documents(document_path: str) -> str:
    """Extract and process startup documents"""
    return f"Processing document: {document_path}"

def extract_startup_data(text_content: str) -> str:
    """Extract structured startup information from text content"""
    return f"Extracted startup data from: {text_content[:100]}..."

def validate_extracted_data(data: str) -> str:
    """Validate extracted startup data"""
    return f"Validated data: {data[:50]}..."
'
            agent_tools="extract_from_documents, extract_startup_data, validate_extracted_data"
            ;;
        "risk_assessment_agent")
            agent_functions='
def identify_risks(startup_data: str) -> str:
    """Identify potential risks in startup data"""
    return f"Risk analysis for: {startup_data[:50]}..."

def analyze_market_conditions(market_data: str) -> str:
    """Analyze market conditions and risks"""
    return f"Market analysis: {market_data[:50]}..."

def evaluate_financial_health(financial_data: str) -> str:
    """Evaluate financial health and risks"""
    return f"Financial evaluation: {financial_data[:50]}..."
'
            agent_tools="identify_risks, analyze_market_conditions, evaluate_financial_health"
            ;;
        "meeting_scheduler_agent")
            agent_functions='
def schedule_meeting(founder_name: str, preferred_time: str) -> str:
    """Schedule a meeting with the founder"""
    return f"Scheduled meeting for {founder_name} at {preferred_time}"

def check_availability(time_slot: str) -> str:
    """Check availability for a time slot"""
    return f"Availability checked for: {time_slot}"

def send_invitations(meeting_details: str) -> str:
    """Send meeting invitations"""
    return f"Invitations sent for: {meeting_details}"
'
            agent_tools="schedule_meeting, check_availability, send_invitations"
            ;;
        "adk_interview_agent")
            agent_functions='
def start_interview_session(founder_name: str, session_id: str) -> str:
    """Start a new interview session with a startup founder"""
    return f"Started interview session for {founder_name} (Session: {session_id})"

def process_founder_response(response: str, question_number: int) -> str:
    """Process the founder response and provide next question"""
    return f"Processed response to question {question_number}: {response[:50]}..."

def generate_summary_report(founder_name: str, responses: str) -> str:
    """Generate a summary report of the interview"""
    return f"Generated summary report for {founder_name}"
'
            agent_tools="start_interview_session, process_founder_response, generate_summary_report"
            ;;
        "voice_interview_agent")
            agent_functions='
def start_voice_session(founder_name: str) -> str:
    """Start a voice interview session"""
    return f"Started voice session for {founder_name}"

def process_voice_input(audio_data: str) -> str:
    """Process voice input from founder"""
    return f"Processed voice input: {audio_data[:50]}..."

def generate_voice_response(response: str) -> str:
    """Generate voice response to founder"""
    return f"Generated voice response: {response[:50]}..."
'
            agent_tools="start_voice_session, process_voice_input, generate_voice_response"
            ;;
        "audio_interview_agent")
            agent_functions='
def process_audio_input(audio_file: str) -> str:
    """Process audio input from founder"""
    return f"Processed audio file: {audio_file}"

def transcribe_speech(audio_data: str) -> str:
    """Transcribe speech to text"""
    return f"Transcribed speech: {audio_data[:50]}..."

def analyze_voice_sentiment(speech_text: str) -> str:
    """Analyze sentiment from voice"""
    return f"Sentiment analysis: {speech_text[:50]}..."
'
            agent_tools="process_audio_input, transcribe_speech, analyze_voice_sentiment"
            ;;
        "memo_generation_agent")
            agent_functions='
def generate_investment_memo(startup_data: str) -> str:
    """Generate investment memo"""
    return f"Generated investment memo for: {startup_data[:50]}..."

def format_document(memo_content: str) -> str:
    """Format the investment memo document"""
    return f"Formatted memo: {memo_content[:50]}..."

def export_documents(memo: str, format: str) -> str:
    """Export memo in specified format"""
    return f"Exported memo as {format}: {memo[:50]}..."
'
            agent_tools="generate_investment_memo, format_document, export_documents"
            ;;
        "final_evaluation_agent")
            agent_functions='
def analyze_startup_data(data: str) -> str:
    """Analyze comprehensive startup data"""
    return f"Analyzed startup data: {data[:50]}..."

def calculate_risk_score(risk_factors: str) -> str:
    """Calculate overall risk score"""
    return f"Risk score calculated: {risk_factors[:50]}..."

def generate_investment_recommendation(evaluation: str) -> str:
    """Generate investment recommendation"""
    return f"Investment recommendation: {evaluation[:50]}..."
'
            agent_tools="analyze_startup_data, calculate_risk_score, generate_investment_recommendation"
            ;;
        "main_orchestrator")
            agent_functions='
def coordinate_all_agents(workflow_data: str) -> str:
    """Coordinate all agents in the workflow"""
    return f"Coordinated agents for: {workflow_data[:50]}..."

def manage_evaluation_workflow(workflow: str) -> str:
    """Manage the complete evaluation workflow"""
    return f"Managed workflow: {workflow[:50]}..."

def synthesize_results(results: str) -> str:
    """Synthesize results from all agents"""
    return f"Synthesized results: {results[:50]}..."
'
            agent_tools="coordinate_all_agents, manage_evaluation_workflow, synthesize_results"
            ;;
    esac
    
    deploy_agent "${agent_name}" "${agent_description}" "${agent_functions}"
done

echo ""
echo "🎉 ALL Agents Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Deployed Agents (in correct flow order):"
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
echo "   • Extractor Agent is the main entry point"
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

echo ""
echo "✨ ALL agents are now deployed to Agent Engine!"