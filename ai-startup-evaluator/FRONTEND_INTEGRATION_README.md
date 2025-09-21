# Frontend Integration with ADK Interview Agent

This document describes the frontend integration with the deployed ADK Interview Agent on Google Cloud Agent Engine.

## 🎯 Overview

The frontend now includes a complete interview chatbot interface that allows startup founders to interact directly with the deployed ADK Interview Agent. The integration provides:

- **Real-time chat interface** with the AI Interview Agent
- **Investment-focused questioning** covering all key areas
- **Live sentiment analysis** and confidence scoring
- **Dynamic follow-up questions** based on responses
- **Comprehensive evaluation reports** stored in GCS

## 🏗️ Architecture

```
Frontend (React) → Backend API (FastAPI) → Agent Engine (Google Cloud)
     ↓                    ↓                        ↓
InterviewChat.js → agent_api.py → Deployed ADK Agent
```

## 📁 New Files Created

### Frontend Components
- `frontend/src/components/InterviewChatbot.js` - Main chatbot component
- `frontend/src/pages/InterviewChat.js` - Interview chat page with stepper
- Updated `frontend/src/App.js` - Added new route
- Updated `frontend/src/components/Navbar.js` - Added AI Interview link

### Backend API
- `backend/api/agent_api.py` - API endpoints for Agent Engine integration
- Updated `backend/main.py` - Included agent router
- Updated `backend/requirements.txt` - Added Vertex AI dependencies

### Testing & Documentation
- `test_frontend_integration.py` - Integration test script
- `FRONTEND_INTEGRATION_README.md` - This documentation

## 🚀 Getting Started

### 1. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 2. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Start the Frontend

```bash
cd frontend
npm start
```

### 4. Access the Interview Chat

1. Open http://localhost:3000 in your browser
2. Click on "AI Interview" in the navigation bar
3. Enter founder and startup details
4. Start the conversation with the AI agent

## 🔧 API Endpoints

The backend now includes the following agent-related endpoints:

### Start Interview
```http
POST /api/agent/start-interview
Content-Type: application/json

{
  "founder_name": "John Doe",
  "startup_name": "FoodTech Inc"
}
```

### Process Response
```http
POST /api/agent/process-response
Content-Type: application/json

{
  "session_id": "session_123",
  "response": "We're solving food waste..."
}
```

### Get Interview Status
```http
GET /api/agent/status/{session_id}
```

### Generate Report
```http
POST /api/agent/generate-report/{session_id}
```

### Health Check
```http
GET /api/agent/health
```

## 🎨 UI Features

### Interview Chat Interface
- **Real-time messaging** with typing indicators
- **Message history** with timestamps
- **Sentiment analysis** display with color coding
- **Confidence scoring** for each response
- **Progress tracking** with stepper component

### Sidebar Information
- **Investment focus areas** overview
- **AI analysis features** explanation
- **Expected duration** and process info

### Results Dialog
- **Session summary** with key metrics
- **Analysis results** with sentiment and confidence
- **Report generation** option

## 🔄 Interview Flow

1. **Start Interview**
   - Enter founder name and startup name
   - Agent generates greeting and first question

2. **Conduct Interview**
   - Answer 6 core investment questions
   - Receive dynamic follow-up questions
   - See real-time analysis of responses

3. **Review Results**
   - View session summary
   - Check sentiment and confidence scores
   - Review key insights and red flags

4. **Generate Report**
   - Create comprehensive evaluation report
   - Store in Google Cloud Storage
   - Access for downstream analytics

## 🧪 Testing

Run the integration test to verify everything is working:

```bash
python test_frontend_integration.py
```

This will test:
- Backend API health
- Agent Engine connectivity
- Interview session flow
- Frontend accessibility

## 🔐 Authentication & Security

The integration uses:
- **Google Cloud authentication** for Agent Engine access
- **CORS configuration** for frontend-backend communication
- **Session management** for interview tracking
- **Error handling** with user-friendly messages

## 📊 Data Flow

1. **Frontend** sends interview request to backend
2. **Backend** calls Agent Engine with session details
3. **Agent Engine** processes with deployed ADK agent
4. **Response** includes next question and analysis
5. **Frontend** displays message and updates UI
6. **Final report** stored in GCS for analytics

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**
   ```bash
   # Check if port 8000 is available
   lsof -i :8000
   ```

2. **Agent Engine connection failed**
   ```bash
   # Verify Google Cloud authentication
   gcloud auth application-default login
   ```

3. **Frontend not loading**
   ```bash
   # Check if React dev server is running
   cd frontend && npm start
   ```

4. **CORS errors**
   - Ensure backend CORS is configured for localhost:3000
   - Check if frontend is running on correct port

### Debug Mode

Enable debug logging in the backend:

```bash
export DEBUG=true
uvicorn main:app --reload --port 8000
```

## 🚀 Deployment

### Backend Deployment
The backend can be deployed to Google Cloud Run:

```bash
# Build and deploy
gcloud run deploy ai-startup-evaluator-api \
  --source backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend Deployment
The frontend can be deployed to Firebase Hosting or similar:

```bash
cd frontend
npm run build
# Deploy build folder to your hosting service
```

## 📈 Future Enhancements

- **Voice input/output** integration
- **Multi-language support** for international founders
- **Advanced analytics dashboard** for interview insights
- **Integration with CRM systems** for lead management
- **Mobile app** for on-the-go interviews

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run the integration test
3. Review the logs for error details
4. Create an issue with detailed information

---

**Note**: This integration requires the ADK Interview Agent to be deployed on Google Cloud Agent Engine. Make sure the deployment is successful before testing the frontend integration.