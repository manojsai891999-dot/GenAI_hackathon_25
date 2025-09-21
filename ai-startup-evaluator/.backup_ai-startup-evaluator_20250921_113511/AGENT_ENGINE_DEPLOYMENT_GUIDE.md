# ADK Interview Agent - Agent Engine Deployment Guide

This guide walks you through deploying the ADK Interview Agent to Google Cloud's Agent Engine following the [official ADK deployment documentation](https://google.github.io/adk-docs/deploy/agent-engine/#deploy-to-agent-engine).

## 🎯 Overview

The ADK Interview Agent is designed to conduct investment-focused interviews with startup founders, featuring:
- **CloudSQL Integration**: Stores all responses in `startup-evaluator-db` database
- **GCS Integration**: Generates and stores comprehensive reports
- **Real-time Analysis**: Sentiment analysis, confidence scoring, and insight extraction
- **Dynamic Follow-ups**: Intelligent follow-up questions based on response quality

## 📋 Prerequisites

Before deploying, ensure you have the following installed:

### Required Tools
- **Python 3.9-3.13**: [Python Installation](https://www.python.org/downloads/)
- **UV Tool**: [Install UV](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud CLI**: [Install gcloud](https://cloud.google.com/sdk/docs/install)
- **Make Tool**: Usually pre-installed on Unix systems
- **Terraform**: [Install Terraform](https://developer.hashicorp.com/terraform/downloads)

### Google Cloud Setup
- **Google Cloud Account** with billing enabled
- **Empty Google Cloud Project** (or project with Agent Engine API enabled)
- **CloudSQL Instance**: `startup-evaluator-db` with database `startup_evaluator`
- **GCS Bucket**: `startup-evaluator-storage` for report storage

## 🚀 Deployment Steps

### Step 1: Prepare Your Environment

```bash
# Clone or navigate to the project directory
cd ai-startup-evaluator

# Verify prerequisites
python deploy_to_agent_engine.py
```

### Step 2: Authenticate with Google Cloud

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
```

### Step 3: Prepare the ADK Project

The Agent Starter Pack (ASP) will enhance your project with deployment artifacts:

```bash
# Run ASP enhance command
uvx agent-starter-pack enhance --adk -d agent_engine

# Follow the prompts:
# - GCP Region: us-central1 (or your preferred region)
# - Accept defaults for other options
```

This command will:
- Add deployment configuration files
- Create a Makefile for deployment
- Set up Terraform configurations
- Prepare the project for Agent Engine deployment

### Step 4: Deploy to Agent Engine

```bash
# Deploy using the generated Makefile
make deploy
```

Or use the automated deployment script:

```bash
python deploy_to_agent_engine.py
```

### Step 5: Verify Deployment

```bash
# Check deployed agents
gcloud ai reasoning-engines list --location=us-central1

# Test the deployed agent
python test_deployed_agent.py
```

## 🧪 Testing Your Deployed Agent

### Using REST API

1. **Create a Session**:
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/reasoningEngines/YOUR_AGENT_ID:query \
  -d '{
    "class_method": "start_interview_session",
    "input": {
      "founder_name": "Sarah Johnson",
      "startup_name": "EcoTech Solutions"
    }
  }'
```

2. **Process Founder Response**:
```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/reasoningEngines/YOUR_AGENT_ID:streamQuery?alt=sse \
  -d '{
    "class_method": "process_founder_response",
    "input": {
      "session_id": "YOUR_SESSION_ID",
      "response": "We are solving food waste in supply chains..."
    }
  }'
```

### Using Python Client

```python
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
```

## 🔧 Configuration

### Environment Variables

The agent uses the following environment variables:

```env
# Database Configuration
DATABASE_URL=postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db

# Cloud Storage
GCS_BUCKET_NAME=startup-evaluator-storage

# Debug Mode
DEBUG=false
```

### Agent Configuration

The `agent_config.yaml` file contains:
- Agent capabilities and tools
- Model configuration (Gemini 2.0 Flash)
- Interview question definitions
- CloudSQL and GCS settings
- Deployment parameters

## 📊 Monitoring and Management

### Google Cloud Console

1. **Agent Engine Dashboard**: 
   - Navigate to [Agent Engine Console](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
   - View agent status, metrics, and logs

2. **CloudSQL Monitoring**:
   - Check database performance and connections
   - Monitor query execution and storage usage

3. **GCS Monitoring**:
   - View report generation and storage metrics
   - Monitor bucket usage and access patterns

### Logging and Debugging

```bash
# View agent logs
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" --limit=50

# View specific agent logs
gcloud logging read "resource.labels.reasoning_engine_id=YOUR_AGENT_ID" --limit=50
```

## 🔄 Updating the Agent

To update your deployed agent:

1. **Modify your code** in the project directory
2. **Redeploy** using the same process:
   ```bash
   make deploy
   ```
3. **Verify the update** using the test script

## 🧹 Cleanup

To remove the deployed agent and associated resources:

```bash
# Delete the agent
gcloud ai reasoning-engines delete YOUR_AGENT_ID --location=us-central1

# Or use the Python client
remote_app.delete(force=True)
```

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Permission Errors**:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="user:YOUR_EMAIL" \
     --role="roles/aiplatform.user"
   ```

3. **Database Connection Issues**:
   - Verify CloudSQL instance is running
   - Check firewall rules and network connectivity
   - Ensure proper authentication credentials

4. **Deployment Failures**:
   - Check all prerequisites are installed
   - Verify Google Cloud project has billing enabled
   - Ensure required APIs are enabled

### Getting Help

- **ADK Documentation**: [https://google.github.io/adk-docs/](https://google.github.io/adk-docs/)
- **Agent Engine Documentation**: [https://cloud.google.com/vertex-ai/docs/agent-builder/overview](https://cloud.google.com/vertex-ai/docs/agent-builder/overview)
- **Google Cloud Support**: [https://cloud.google.com/support](https://cloud.google.com/support)

## 📈 Performance Optimization

### Scaling Configuration

The agent is configured for:
- **Min Instances**: 1
- **Max Instances**: 10
- **Memory**: 2GB
- **CPU**: 2 cores
- **Timeout**: 300 seconds

### Database Optimization

- Use connection pooling for CloudSQL
- Implement proper indexing for query performance
- Monitor and optimize slow queries

### Storage Optimization

- Use appropriate GCS storage classes
- Implement lifecycle policies for report retention
- Monitor storage costs and usage

## 🎉 Success!

Once deployed, your ADK Interview Agent will be available at:
- **Agent Engine Console**: [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
- **REST API**: Available through the Agent Engine API
- **Python Client**: Accessible via the ADK Python client

The agent will automatically:
- Conduct investment interviews with startup founders
- Store all responses in CloudSQL
- Generate comprehensive reports in GCS
- Provide real-time analysis and insights