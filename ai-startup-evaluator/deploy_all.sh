#!/bin/bash

# Deploy Complete Application to Google Cloud Run
# This script deploys both backend and frontend to Cloud Run

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
BACKEND_SERVICE="ai-startup-evaluator-api"
FRONTEND_SERVICE="ai-startup-evaluator-frontend"
REGION="us-central1"

echo "🚀 Deploying Complete Application to Google Cloud Run"
echo "===================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Backend Service: ${BACKEND_SERVICE}"
echo "Frontend Service: ${FRONTEND_SERVICE}"
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
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Deploy Backend
echo ""
echo "🏗️ Deploying Backend..."
echo "======================="
cd backend
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${BACKEND_SERVICE} .
gcloud run deploy ${BACKEND_SERVICE} \
    --image gcr.io/${PROJECT_ID}/${BACKEND_SERVICE} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}" \
    --set-cloudsql-instances "${PROJECT_ID}:${REGION}:startup-evaluator-db"

# Get backend URL
BACKEND_URL=$(gcloud run services describe ${BACKEND_SERVICE} --platform managed --region ${REGION} --format 'value(status.url)')
echo "✅ Backend deployed: ${BACKEND_URL}"

# Deploy Frontend
echo ""
echo "🏗️ Deploying Frontend..."
echo "========================"
cd ../frontend

# Update nginx configuration with backend URL
echo "🔧 Updating nginx configuration with backend URL..."
sed -i.bak "s|https://ai-startup-evaluator-api-xxxxxxxxx-uc.a.run.app|${BACKEND_URL}|g" nginx.conf

# Build and deploy frontend
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE} .
gcloud run deploy ${FRONTEND_SERVICE} \
    --image gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 1000

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe ${FRONTEND_SERVICE} --platform managed --region ${REGION} --format 'value(status.url)')
echo "✅ Frontend deployed: ${FRONTEND_URL}"

# Update backend CORS with frontend URL
echo ""
echo "🔧 Updating backend CORS configuration..."
cd ../backend
# This would require updating the main.py file with the actual frontend URL
echo "⚠️  Please manually update the CORS configuration in backend/main.py with:"
echo "   Frontend URL: ${FRONTEND_URL}"

# Restore nginx configuration
cd ../frontend
if [ -f "nginx.conf.bak" ]; then
    mv nginx.conf.bak nginx.conf
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "Backend URL:  ${BACKEND_URL}"
echo "Frontend URL: ${FRONTEND_URL}"
echo ""
echo "📝 Next steps:"
echo "1. Update backend CORS configuration with frontend URL"
echo "2. Test the application at: ${FRONTEND_URL}"
echo "3. Access the AI Interview Chat at: ${FRONTEND_URL}/interview-chat"
echo ""
echo "🔧 To update CORS, run:"
echo "   gcloud run services update ${BACKEND_SERVICE} --region ${REGION} --update-env-vars FRONTEND_URL=${FRONTEND_URL}"

cd ..