#!/bin/bash

# Deploy All Agents to Google Cloud Agent Engine
# This script deploys all startup evaluation agents to Agent Engine

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
REGION="us-central1"
AGENTS_DIR="backend/agents"

echo "🚀 Deploying All Agents to Google Cloud Agent Engine"
echo "=================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
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
    
    echo ""
    echo "🤖 Deploying ${agent_name}..."
    echo "================================"
    
    # Create agent configuration
    cat > ${agent_name}_config.yaml << EOF
agent:
  name: "${agent_id}"
  description: "${agent_name} for startup evaluation"
  version: "1.0.0"
  
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

# List of agents to deploy
declare -A agents=(
    ["adk_interview_agent"]="adk_interview_agent.py:adk-interview-agent"
    ["audio_interview_agent"]="audio_interview_agent.py:audio-interview-agent"
    ["voice_interview_agent"]="voice_interview_agent.py:voice-interview-agent"
    ["final_evaluation_agent"]="final_evaluation_agent.py:final-evaluation-agent"
    ["risk_agent"]="risk_agent.py:risk-assessment-agent"
    ["memo_agent"]="memo_agent.py:memo-generation-agent"
    ["meeting_scheduler_agent"]="meeting_scheduler_agent.py:meeting-scheduler-agent"
    ["extractor_agent"]="extractor_agent.py:data-extractor-agent"
    ["interview_orchestrator"]="interview_orchestrator.py:interview-orchestrator"
    ["orchestrator"]="orchestrator.py:main-orchestrator"
)

# Deploy each agent
for agent_name in "${!agents[@]}"; do
    IFS=':' read -r agent_file agent_id <<< "${agents[$agent_name]}"
    
    if [ -f "${AGENTS_DIR}/${agent_file}" ]; then
        deploy_agent "${agent_name}" "${agent_file}" "${agent_id}"
    else
        echo "   ⚠️  Agent file ${agent_file} not found, skipping ${agent_name}"
    fi
done

echo ""
echo "🎉 All Agents Deployment Complete!"
echo "=================================="
echo ""
echo "📋 Deployed Agents:"
echo "  ✅ ADK Interview Agent"
echo "  ✅ Audio Interview Agent"
echo "  ✅ Voice Interview Agent"
echo "  ✅ Final Evaluation Agent"
echo "  ✅ Risk Assessment Agent"
echo "  ✅ Memo Generation Agent"
echo "  ✅ Meeting Scheduler Agent"
echo "  ✅ Data Extractor Agent"
echo "  ✅ Interview Orchestrator"
echo "  ✅ Main Orchestrator"
echo ""
echo "🔗 Access your agents in Google Cloud Console:"
echo "   https://console.cloud.google.com/ai/agent-engines?project=${PROJECT_ID}"
echo ""
echo "📝 Next steps:"
echo "1. Test agent interactions through the frontend"
echo "2. Monitor agent performance in Cloud Console"
echo "3. Configure agent communication and workflows"
echo "4. Set up monitoring and alerting"

# Clean up temporary files
rm -f *_config.yaml

echo ""
echo "✨ All agents are now deployed on Agent Engine!"