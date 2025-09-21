# AI-Powered Startup Evaluation Platform

An intelligent platform that automates 80-90% of early-stage startup curation for investors using Google Cloud AI agents.

## Architecture Overview

### Backend (Python/FastAPI)
- **Google ADK Agents**: 7 specialized AI agents for different evaluation tasks
- **Cloud SQL**: Structured data storage (PostgreSQL)
- **Google Cloud Storage**: Unstructured data (PDFs, audio, transcripts)
- **FastAPI**: RESTful API layer

### Frontend (ReactJS)
- Modern dashboard interface
- Multi-page evaluation workflow
- Real-time data visualization
- File upload and management

## Project Structure

```
ai-startup-evaluator/
├── backend/
│   ├── agents/              # Google ADK agents
│   ├── api/                 # FastAPI routes
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   └── main.py              # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Dashboard pages
│   │   ├── services/        # API calls
│   │   └── utils/           # Frontend utilities
│   └── public/
├── docs/                    # Documentation
└── deployment/              # Deployment configs
```

## Features

### AI Agents
1. **ExtractorAgent** - Parse pitch decks and forms
2. **PublicDataExtractorAgent** - Gather market benchmarks
3. **RiskAgent** - Identify investment risks
4. **MemoAgent** - Generate investor memos
5. **MeetingSchedulerAgent** - Schedule meetings
6. **VoiceInterviewAgent** - Process founder interviews
7. **FinalEvaluationAgent** - Calculate investment scores

### Dashboard Pages
- Startup Overview
- Founder Profiles
- Market Benchmarks
- Risk Assessment
- Interview Analysis
- Investment Memo
- Final Evaluation

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- Google Cloud Project with enabled APIs
- PostgreSQL database

### Installation

1. Clone and setup backend:
```bash
cd backend
pip install -r requirements.txt
```

2. Setup frontend:
```bash
cd frontend
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Google Cloud credentials
```

### Running the Application

1. Start backend:
```bash
cd backend
uvicorn main:app --reload
```

2. Start frontend:
```bash
cd frontend
npm start
```

## API Endpoints

- `GET /api/startup/{startup_id}` - Basic startup info
- `GET /api/startup/{startup_id}/founders` - Founder details
- `GET /api/startup/{startup_id}/benchmarks` - Market comparisons
- `GET /api/startup/{startup_id}/risks` - Risk assessment
- `GET /api/startup/{startup_id}/interview` - Interview summary
- `GET /api/startup/{startup_id}/final` - Final evaluation

## Deployment

The platform is designed for Google Cloud Platform deployment using:
- Cloud Run for containerized services
- Cloud SQL for PostgreSQL
- Cloud Storage for file storage
- Cloud Build for CI/CD

## License

MIT License
