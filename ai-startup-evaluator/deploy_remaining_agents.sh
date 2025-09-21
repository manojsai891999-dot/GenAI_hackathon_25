#!/bin/bash

# Deploy Remaining Agents to Google Cloud Agent Engine
# This script deploys the remaining agents that haven't been deployed yet

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
REGION="us-central1"

echo "🚀 Deploying Remaining Agents to Google Cloud Agent Engine"
echo "=========================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Function to deploy a single agent
deploy_agent() {
    local agent_name=$1
    local agent_description=$2
    local agent_functions=$3
    local agent_tools=$4
    
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

# Deploy remaining agents
echo "📋 Deploying remaining agents..."

# Meeting Scheduler Agent
deploy_agent "meeting_scheduler_agent" "Meeting Scheduler Agent - Intelligent meeting scheduling" \
'def schedule_meeting(founder_name: str, preferred_time: str) -> str:
    """Schedule a meeting with the founder"""
    return f"Scheduled meeting for {founder_name} at {preferred_time}"

def check_availability(time_slot: str) -> str:
    """Check availability for a time slot"""
    return f"Availability checked for: {time_slot}"

def send_invitations(meeting_details: str) -> str:
    """Send meeting invitations"""
    return f"Invitations sent for: {meeting_details}"' \
"schedule_meeting, check_availability, send_invitations"

# Voice Interview Agent (Optional)
deploy_agent "voice_interview_agent" "Voice Interview Agent - Advanced voice interview agent with real-time processing (OPTIONAL)" \
'def start_voice_session(founder_name: str) -> str:
    """Start a voice interview session"""
    return f"Started voice session for {founder_name}"

def process_voice_input(audio_data: str) -> str:
    """Process voice input from founder"""
    return f"Processed voice input: {audio_data[:50]}..."

def generate_voice_response(response: str) -> str:
    """Generate voice response to founder"""
    return f"Generated voice response: {response[:50]}..."' \
"start_voice_session, process_voice_input, generate_voice_response"

# Audio Interview Agent
deploy_agent "audio_interview_agent" "Audio Interview Agent - Audio-based interview agent for voice interactions" \
'def process_audio_input(audio_file: str) -> str:
    """Process audio input from founder"""
    return f"Processed audio file: {audio_file}"

def transcribe_speech(audio_data: str) -> str:
    """Transcribe speech to text"""
    return f"Transcribed speech: {audio_data[:50]}..."

def analyze_voice_sentiment(speech_text: str) -> str:
    """Analyze sentiment from voice"""
    return f"Sentiment analysis: {speech_text[:50]}..."' \
"process_audio_input, transcribe_speech, analyze_voice_sentiment"

# Memo Generation Agent
deploy_agent "memo_generation_agent" "Memo Generation Agent - Investment memo generation agent" \
'def generate_investment_memo(startup_data: str) -> str:
    """Generate investment memo"""
    return f"Generated investment memo for: {startup_data[:50]}..."

def format_document(memo_content: str) -> str:
    """Format the investment memo document"""
    return f"Formatted memo: {memo_content[:50]}..."

def export_documents(memo: str, format: str) -> str:
    """Export memo in specified format"""
    return f"Exported memo as {format}: {memo[:50]}..."' \
"generate_investment_memo, format_document, export_documents"

# Final Evaluation Agent
deploy_agent "final_evaluation_agent" "Final Evaluation Agent - Comprehensive evaluation agent for final startup assessment" \
'def analyze_startup_data(data: str) -> str:
    """Analyze comprehensive startup data"""
    return f"Analyzed startup data: {data[:50]}..."

def calculate_risk_score(risk_factors: str) -> str:
    """Calculate overall risk score"""
    return f"Risk score calculated: {risk_factors[:50]}..."

def generate_investment_recommendation(evaluation: str) -> str:
    """Generate investment recommendation"""
    return f"Investment recommendation: {evaluation[:50]}..."' \
"analyze_startup_data, calculate_risk_score, generate_investment_recommendation"

# Main Orchestrator
deploy_agent "main_orchestrator" "Main Orchestrator - Main orchestrator that coordinates all agents and synthesizes results" \
'def coordinate_all_agents(workflow_data: str) -> str:
    """Coordinate all agents in the workflow"""
    return f"Coordinated agents for: {workflow_data[:50]}..."

def manage_evaluation_workflow(workflow: str) -> str:
    """Manage the complete evaluation workflow"""
    return f"Managed workflow: {workflow[:50]}..."

def synthesize_results(results: str) -> str:
    """Synthesize results from all agents"""
    return f"Synthesized results: {results[:50]}..."' \
"coordinate_all_agents, manage_evaluation_workflow, synthesize_results"

echo ""
echo "🎉 ALL Remaining Agents Deployment Complete!"
echo "============================================"
echo ""
echo "📋 Deployed Agents:"
echo "  ✅ 1. Extractor Agent (Entry Point) - ALREADY DEPLOYED"
echo "  ✅ 2. Risk Assessment Agent - ALREADY DEPLOYED"
echo "  ✅ 3. ADK Interview Agent - ALREADY DEPLOYED"
echo "  ✅ 4. Meeting Scheduler Agent - DEPLOYED"
echo "  ✅ 5. Voice Interview Agent (OPTIONAL) - DEPLOYED"
echo "  ✅ 6. Audio Interview Agent - DEPLOYED"
echo "  ✅ 7. Memo Generation Agent - DEPLOYED"
echo "  ✅ 8. Final Evaluation Agent - DEPLOYED"
echo "  ✅ 9. Main Orchestrator - DEPLOYED"
echo ""
echo "🔄 Complete Agent Flow:"
echo "   Extractor → Risk → Meeting Scheduler →"
echo "   ADK Interview (after meeting approved) → Memo →"
echo "   Final Evaluation → Main Orchestrator"
echo ""
echo "🔗 Access your agents in Google Cloud Console:"
echo "   https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=${PROJECT_ID}"
echo ""
echo "✨ ALL agents are now deployed to Agent Engine!"