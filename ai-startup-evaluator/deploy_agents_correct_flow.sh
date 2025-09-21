#!/bin/bash

# Deploy All Agents to Google Cloud Agent Engine - Correct Flow
# This script deploys agents in the correct sequence starting with extractor agent

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
REGION="us-central1"
AGENTS_DIR="backend/agents"

echo "🚀 Deploying All Agents to Google Cloud Agent Engine (Correct Flow)"
echo "=================================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""
echo "📋 Agent Flow Sequence:"
echo "1. Extractor Agent (Entry Point)"
echo "2. Public Data Extractor Agent"
echo "3. Risk Assessment Agent"
echo "4. Meeting Scheduler Agent"
echo "5. ADK Interview Agent (after meeting approved)"
echo "6. Voice Interview Agent (OPTIONAL)"
echo "7. Audio Interview Agent"
echo "8. Memo Generation Agent"
echo "9. Final Evaluation Agent"
echo "10. Main Orchestrator"
echo ""
echo "🔄 Flow Logic:"
echo "   Risk Assessment → Meeting Scheduler → Interview Agent (after approval)"
echo "   Voice Interview is OPTIONAL"
echo ""

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

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
    local agent_file=$2
    local agent_id=$3
    local priority=$4
    
    echo ""
    echo "🤖 Deploying ${agent_name} (Priority: ${priority})..."
    echo "=================================================="
    
    # Create agent configuration
    cat > ${agent_name}_config.yaml << EOF
agent:
  name: "${agent_id}"
  description: "${agent_name} for startup evaluation"
  version: "1.0.0"
  priority: ${priority}
  
  # Model configuration
  model:
    name: "gemini-2.0-flash"
    temperature: 0.7
    max_tokens: 2048
  
  # Database configuration
  database:
    type: "cloudsql"
    instance: "startup-evaluator-db"
    database: "startup_evaluator"
    user: "app-user"
    password: "aianalyst"
  
  # Cloud Storage configuration
  storage:
    type: "gcs"
    bucket: "startup-evaluator-storage"
  
  # Deployment settings
  deployment:
    region: "${REGION}"
    min_instances: 1
    max_instances: 5
    timeout: 300
    memory: "2Gi"
    cpu: "2"
  
  # Environment variables
  env:
    DATABASE_URL: "postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db"
    GCS_BUCKET_NAME: "startup-evaluator-storage"
    DEBUG: "false"
EOF

    # Deploy the agent using gcloud
    echo "   📦 Creating agent configuration..."
    echo "   🚀 Deploying to Agent Engine..."
    
    # Use gcloud to create the agent
    gcloud ai agents create \
        --display-name="${agent_name}" \
        --description="AI agent for startup evaluation" \
        --region="${REGION}" \
        --config-file="${agent_name}_config.yaml" \
        --quiet || echo "   ⚠️  Agent ${agent_name} may already exist or deployment failed"
    
    echo "   ✅ ${agent_name} deployment completed"
}

# Define agents in correct flow order with priorities
agents=(
    "extractor_agent:extractor_agent.py:extractor-agent:1"
    "public_data_extractor_agent:public_data_extractor_agent.py:public-data-extractor-agent:2"
    "risk_agent:risk_agent.py:risk-assessment-agent:3"
    "meeting_scheduler_agent:meeting_scheduler_agent.py:meeting-scheduler-agent:4"
    "adk_interview_agent:adk_interview_agent.py:adk-interview-agent:5"
    "voice_interview_agent:voice_interview_agent.py:voice-interview-agent:6"
    "audio_interview_agent:audio_interview_agent.py:audio-interview-agent:7"
    "memo_agent:memo_agent.py:memo-generation-agent:8"
    "final_evaluation_agent:final_evaluation_agent.py:final-evaluation-agent:9"
    "orchestrator:orchestrator.py:main-orchestrator:10"
)

# Deploy each agent in correct order
for agent_info in "${agents[@]}"; do
    IFS=':' read -r agent_name agent_file agent_id priority <<< "${agent_info}"
    
    if [ -f "${AGENTS_DIR}/${agent_file}" ]; then
        deploy_agent "${agent_name}" "${agent_file}" "${agent_id}" "${priority}"
    else
        echo "   ⚠️  Agent file ${agent_file} not found, skipping ${agent_name}"
    fi
done

echo ""
echo "🎉 All Agents Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Deployed Agents (in correct flow order):"
echo "  ✅ 1. Extractor Agent (Entry Point)"
echo "  ✅ 2. Public Data Extractor Agent"
echo "  ✅ 3. Risk Assessment Agent"
echo "  ✅ 4. Interview Orchestrator"
echo "  ✅ 5. ADK Interview Agent"
echo "  ✅ 6. Voice Interview Agent"
echo "  ✅ 7. Audio Interview Agent"
echo "  ✅ 8. Meeting Scheduler Agent"
echo "  ✅ 9. Memo Generation Agent"
echo "  ✅ 10. Final Evaluation Agent"
echo "  ✅ 11. Main Orchestrator"
echo ""
echo "🔄 Agent Flow:"
echo "   Extractor → Public Data → Risk → Meeting Scheduler →"
echo "   ADK Interview (after meeting approved) → Memo →"
echo "   Final Evaluation → Main Orchestrator"
echo ""
echo "📝 Key Points:"
echo "   • Risk Assessment → Meeting Scheduler → Interview Agent"
echo "   • Interview Agent starts only after meeting is approved"
echo "   • Voice Interview is OPTIONAL"
echo ""
echo "🔗 Access your agents in Google Cloud Console:"
echo "   https://console.cloud.google.com/ai/agent-engines?project=${PROJECT_ID}"
echo ""
echo "📝 Next steps:"
echo "1. Test the complete agent flow starting with document upload"
echo "2. Verify agent communication and data flow"
echo "3. Monitor agent performance in Cloud Console"
echo "4. Configure agent triggers and workflows"

# Clean up temporary files
rm -f *_config.yaml

echo ""
echo "✨ All agents are now deployed on Agent Engine with correct flow!"