# Cloud Run Deployment Guide

This guide explains how to deploy the AI Startup Evaluator application to Google Cloud Run, while keeping the AI agents on Agent Engine.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Agent Engine   │
│   (Cloud Run)   │◄──►│   (Cloud Run)   │◄──►│  (ADK Agents)   │
│   React App     │    │   FastAPI       │    │  Interview AI   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   CloudSQL      │    │   GCS Reports   │
│   (Nginx)       │    │   PostgreSQL    │    │   JSON/Text     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

1. **Google Cloud Project**: `ai-analyst-startup-eval`
2. **Required APIs Enabled**:
   - Cloud Run API
   - Cloud Build API
   - Cloud SQL Admin API
   - AI Platform API
3. **gcloud CLI** installed and authenticated
4. **Docker** installed (for local testing)
5. **CloudSQL Instance**: `startup-evaluator-db` (already created)
6. **Agent Engine**: ADK Interview Agent deployed (already done)

## 🚀 Quick Deployment

### Option 1: Deploy Everything at Once
```bash
./deploy_all.sh
```

### Option 2: Deploy Services Individually
```bash
# Deploy backend first
./deploy_backend.sh

# Then deploy frontend
./deploy_frontend.sh
```

## 📁 Project Structure

```
ai-startup-evaluator/
├── backend/
│   ├── Dockerfile              # Backend container config
│   ├── .dockerignore           # Files to exclude from build
│   ├── main.py                 # FastAPI application
│   ├── api/agent_api.py        # Agent Engine integration
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── Dockerfile              # Frontend container config
│   ├── .dockerignore           # Files to exclude from build
│   ├── nginx.conf              # Nginx configuration
│   ├── src/                    # React source code
│   └── package.json            # Node.js dependencies
├── deploy_backend.sh           # Backend deployment script
├── deploy_frontend.sh          # Frontend deployment script
├── deploy_all.sh               # Complete deployment script
└── cloud-run-config.yaml       # Cloud Run service configs
```

## 🔧 Configuration Details

### Backend Configuration
- **Runtime**: Python 3.11
- **Framework**: FastAPI with Uvicorn
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Port**: 8080
- **Environment Variables**:
  - `GOOGLE_CLOUD_PROJECT`: ai-analyst-startup-eval
  - `GOOGLE_CLOUD_LOCATION`: us-central1
  - `PORT`: 8080

### Frontend Configuration
- **Runtime**: Node.js 18 (build) + Nginx (serve)
- **Memory**: 1GB
- **CPU**: 1 vCPU
- **Port**: 8080
- **Static Files**: Served by Nginx
- **API Proxy**: Routes `/api/*` to backend

### Database Configuration
- **CloudSQL Instance**: startup-evaluator-db
- **Database**: startup_evaluator
- **Connection**: Unix socket via Cloud Run
- **SSL**: Disabled (handled by Cloud SQL Proxy)

## 🌐 Service URLs

After deployment, you'll get URLs like:
- **Backend**: `https://ai-startup-evaluator-api-xxxxxxxxx-uc.a.run.app`
- **Frontend**: `https://ai-startup-evaluator-frontend-xxxxxxxxx-uc.a.run.app`

## 🔗 Integration Points

### Frontend → Backend
- Frontend proxies API calls to backend via Nginx
- CORS configured for production domains
- Health checks for service monitoring

### Backend → Agent Engine
- Uses Vertex AI client to call deployed ADK agents
- Session management for interview tracking
- Real-time response processing

### Backend → CloudSQL
- SQLAlchemy ORM for database operations
- Connection pooling for performance
- Automatic table creation on startup

### Backend → GCS
- Report generation and storage
- JSON and text format outputs
- Organized by founder and session

## 🧪 Testing the Deployment

### 1. Health Checks
```bash
# Test backend
curl https://ai-startup-evaluator-api-xxxxxxxxx-uc.a.run.app/health

# Test frontend
curl https://ai-startup-evaluator-frontend-xxxxxxxxx-uc.a.run.app/health
```

### 2. API Endpoints
```bash
# Test agent API
curl https://ai-startup-evaluator-api-xxxxxxxxx-uc.a.run.app/api/agent/health

# Test interview start
curl -X POST https://ai-startup-evaluator-api-xxxxxxxxx-uc.a.run.app/api/agent/start-interview \
  -H "Content-Type: application/json" \
  -d '{"founder_name": "Test Founder", "startup_name": "Test Startup"}'
```

### 3. Frontend Access
- Open the frontend URL in your browser
- Navigate to "AI Interview" section
- Start a test interview session

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   gcloud builds log --stream
   ```

2. **Service Not Starting**
   ```bash
   # Check service logs
   gcloud run services logs ai-startup-evaluator-api --region us-central1
   ```

3. **CORS Errors**
   - Update CORS configuration in `backend/main.py`
   - Redeploy backend service

4. **Database Connection Issues**
   - Verify CloudSQL instance is running
   - Check connection string configuration
   - Ensure proper IAM permissions

5. **Agent Engine Connection**
   - Verify Agent Engine is deployed
   - Check Vertex AI API is enabled
   - Validate authentication credentials

### Debug Commands

```bash
# List all services
gcloud run services list --region us-central1

# Get service details
gcloud run services describe ai-startup-evaluator-api --region us-central1

# View service logs
gcloud run services logs ai-startup-evaluator-api --region us-central1 --limit 50

# Update service configuration
gcloud run services update ai-startup-evaluator-api --region us-central1 --memory 4Gi
```

## 📊 Monitoring and Logging

### Cloud Run Metrics
- Request count and latency
- Error rates and status codes
- Memory and CPU utilization
- Instance count and scaling

### Application Logs
- Structured logging with severity levels
- Request/response logging
- Error tracking and debugging
- Performance metrics

### Health Monitoring
- Liveness probes for container health
- Readiness probes for traffic routing
- Custom health check endpoints
- Alert configuration

## 🔄 Updates and Maintenance

### Updating Services
```bash
# Update backend
cd backend
gcloud builds submit --tag gcr.io/ai-analyst-startup-eval/ai-startup-evaluator-api .
gcloud run deploy ai-startup-evaluator-api --image gcr.io/ai-analyst-startup-eval/ai-startup-evaluator-api

# Update frontend
cd frontend
gcloud builds submit --tag gcr.io/ai-analyst-startup-eval/ai-startup-evaluator-frontend .
gcloud run deploy ai-startup-evaluator-frontend --image gcr.io/ai-analyst-startup-eval/ai-startup-evaluator-frontend
```

### Scaling Configuration
- **Backend**: 0-10 instances, 2 vCPU, 2GB RAM
- **Frontend**: 0-10 instances, 1 vCPU, 1GB RAM
- **Auto-scaling**: Based on request volume
- **Cold starts**: Minimized with min instances

## 💰 Cost Optimization

### Resource Allocation
- Right-sized memory and CPU allocation
- Efficient container images
- Optimized build processes
- Minimal cold start times

### Scaling Policies
- Scale to zero when not in use
- Fast scale-up for traffic spikes
- Efficient resource utilization
- Cost-effective instance types

## 🔐 Security Considerations

### Network Security
- HTTPS only for all communications
- CORS properly configured
- No direct database access from frontend
- Secure API endpoints

### Authentication
- Google Cloud IAM integration
- Service account permissions
- API key management
- Secure credential storage

### Data Protection
- Encrypted data in transit and at rest
- Secure database connections
- Proper access controls
- Audit logging enabled

## 📈 Performance Optimization

### Backend Optimizations
- Connection pooling for database
- Efficient query patterns
- Caching strategies
- Async request handling

### Frontend Optimizations
- Static file caching
- Gzip compression
- CDN integration
- Optimized bundle sizes

### Database Optimizations
- Proper indexing
- Query optimization
- Connection management
- Backup strategies

---

## 🎯 Next Steps

1. **Deploy the services** using the provided scripts
2. **Test the complete application** end-to-end
3. **Configure monitoring** and alerting
4. **Set up CI/CD** for automated deployments
5. **Optimize performance** based on usage patterns

For questions or issues, refer to the troubleshooting section or check the Google Cloud Run documentation.