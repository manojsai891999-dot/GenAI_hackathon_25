#!/bin/bash

# Deploy Frontend to Google Cloud Run
# This script builds and deploys the React frontend to Cloud Run

set -e

# Configuration
PROJECT_ID="ai-analyst-startup-eval"
SERVICE_NAME="ai-startup-evaluator-frontend"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Frontend to Google Cloud Run"
echo "========================================="
echo "Project ID: ${PROJECT_ID}"
echo "Service Name: ${SERVICE_NAME}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE_NAME}"
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

# Get the backend service URL
echo "🔗 Getting backend service URL..."
BACKEND_URL=$(gcloud run services describe ai-startup-evaluator-api --platform managed --region ${REGION} --format 'value(status.url)' 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Backend service not found. Please deploy the backend first using deploy_backend.sh"
    echo "   Or manually set the BACKEND_URL environment variable"
    read -p "Enter backend URL (or press Enter to skip): " BACKEND_URL
fi

# Update nginx configuration with backend URL
if [ ! -z "$BACKEND_URL" ]; then
    echo "🔧 Updating nginx configuration with backend URL: ${BACKEND_URL}"
    sed -i.bak "s|https://ai-startup-evaluator-api-xxxxxxxxx-uc.a.run.app|${BACKEND_URL}|g" frontend/nginx.conf
fi

# Build and push the Docker image
echo "🏗️ Building and pushing Docker image..."
cd frontend
gcloud builds submit --tag ${IMAGE_NAME} .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
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

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

echo ""
echo "✅ Frontend deployed successfully!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "📝 Next steps:"
echo "1. Test the frontend at: ${SERVICE_URL}"
echo "2. Update the backend CORS configuration with the frontend URL"
echo "3. Test the complete application"

cd ..

# Restore nginx configuration
if [ -f "frontend/nginx.conf.bak" ]; then
    mv frontend/nginx.conf.bak frontend/nginx.conf
fi