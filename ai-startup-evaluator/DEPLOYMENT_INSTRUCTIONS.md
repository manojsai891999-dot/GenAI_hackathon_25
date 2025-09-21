# ADK Interview Agent - Deployment Instructions

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
