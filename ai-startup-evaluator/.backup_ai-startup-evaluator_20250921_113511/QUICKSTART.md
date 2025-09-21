# 🚀 Quick Start Guide - Local Development

Get the AI Startup Evaluator running locally in just a few minutes!

## Prerequisites

- **Python 3.9+** (Check: `python --version`)
- **Node.js 16+** (Check: `node --version`)
- **npm** (Check: `npm --version`)

## 🏃‍♂️ Quick Setup (Automated)

1. **Navigate to the project directory:**
   ```bash
   cd /Users/syedubed/CascadeProjects/ai-startup-evaluator
   ```

2. **Run the automated setup:**
   ```bash
   python setup_local.py
   ```

3. **Get a Google AI API Key (Required for AI features):**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create an API key
   - Add it to `backend/.env`:
     ```
     GOOGLE_AI_API_KEY=your-api-key-here
     ```

4. **Start the application:**
   ```bash
   ./start_local.sh
   ```

5. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🛠️ Manual Setup (Step by Step)

### Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create database tables
python -c "
import sys
sys.path.append('.')
from models.database import create_tables
create_tables()
print('Database created!')
"

# Start the backend server
python -m uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm start
```

## 🧪 Testing the Application

### Sample Data
The setup script creates a sample startup "TechCorp AI" for testing:
- **Name:** TechCorp AI
- **Sector:** SaaS
- **Stage:** Seed
- **Founders:** John Smith (CEO), Sarah Johnson (CTO)

### Test Features
1. **Dashboard:** View the sample startup and statistics
2. **Upload:** Try uploading a PDF pitch deck (requires Google AI API key)
3. **Interview Questions:** View the 32+ predefined questions
4. **Analysis:** Explore the different analysis pages

## 📁 Project Structure

```
ai-startup-evaluator/
├── backend/
│   ├── agents/                 # Google ADK agents
│   │   ├── extractor_agent.py
│   │   ├── voice_interview_agent.py  # 32+ predefined questions
│   │   ├── risk_agent.py
│   │   ├── memo_agent.py
│   │   ├── final_evaluation_agent.py
│   │   └── orchestrator.py
│   ├── models/
│   │   ├── database.py         # SQLite configuration
│   │   ├── schemas.py          # Database models
│   │   └── pydantic_models.py  # API models
│   ├── services/
│   │   └── gcs_service.py      # Google Cloud Storage
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt
│   ├── .env                    # Configuration
│   └── startup_evaluator.db    # SQLite database (created automatically)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/              # Dashboard, Upload, Analysis pages
│   │   └── services/           # API integration
│   ├── package.json
│   └── public/
├── setup_local.py              # Automated setup script
├── start_local.sh              # Startup script
└── QUICKSTART.md              # This file
```

## 🔧 Configuration Options

### Environment Variables (backend/.env)

```bash
# Database
DATABASE_URL=sqlite:///./startup_evaluator.db

# Google AI (Required for AI features)
GOOGLE_AI_API_KEY=your-api-key-here

# Google Cloud (Optional - for file storage)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCS_BUCKET_NAME=your-bucket-name

# Google Search (Optional - for public data)
GOOGLE_SEARCH_API_KEY=your-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Development
DEBUG=true
LOG_LEVEL=INFO
```

## 🎯 Key Features to Test

### 1. Interview Questions System
- Navigate to any startup → Interview tab
- Click "View Interview Questions"
- See 32+ questions across 8 categories:
  - Business Model
  - Market Opportunity
  - Traction Metrics
  - Team Execution
  - Financial Planning
  - Product Development
  - Risks & Challenges
  - Vision & Strategy

### 2. Upload & Analysis
- Go to Upload page
- Upload a PDF pitch deck
- Watch the AI agents process the data
- View comprehensive analysis results

### 3. Dashboard Analytics
- View startup statistics
- See recommendation breakdowns
- Explore sector and stage distributions

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill processes on ports 3000 and 8000
   lsof -ti:3000 | xargs kill -9
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database issues:**
   ```bash
   # Delete and recreate database
   rm backend/startup_evaluator.db
   python setup_local.py
   ```

3. **Missing dependencies:**
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

4. **Google AI API errors:**
   - Ensure your API key is valid
   - Check you have credits/quota available
   - Verify the key is properly set in `.env`

## 🚀 Next Steps

1. **Configure Google Cloud Storage** for file uploads
2. **Add authentication** for multi-user support
3. **Deploy to production** using the deployment configs
4. **Customize interview questions** for your specific needs
5. **Add more AI agents** for specialized analysis

## 📞 Support

If you encounter issues:
1. Check the console logs in both backend and frontend
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Try the manual setup steps if automated setup fails

Happy evaluating! 🎉
