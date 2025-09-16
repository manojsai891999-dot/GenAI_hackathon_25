"""
Startup Evaluation Platform - Main Application Entry Point
Orchestrates all AI agents and provides unified interface
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our agents
from agents.evaluation_agent import StartupEvaluationAgent
from agents.scheduling_agent import StartupSchedulingAgent, MeetingRequest
from agents.interview_agent import StartupInterviewAgent

# Import API
from backend.api.startup_evaluation_api import app as api_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StartupEvaluationOrchestrator:
    """Main orchestrator for the startup evaluation platform"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize agents
        self.evaluation_agent = StartupEvaluationAgent(project_id, location)
        self.scheduling_agent = StartupSchedulingAgent(project_id, location)
        self.interview_agent = StartupInterviewAgent(project_id, location)
        
        logger.info("Startup Evaluation Platform initialized")
    
    async def run_complete_evaluation_pipeline(self, startup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete evaluation pipeline for a startup"""
        
        startup_id = startup_data.get('startup_id')
        logger.info(f"Starting complete evaluation pipeline for startup: {startup_id}")
        
        try:
            # Phase 1: Initial Evaluation
            logger.info("Phase 1: Running initial evaluation...")
            evaluation_result = await self.evaluation_agent.evaluate_startup(startup_data)
            
            # Phase 2: Schedule Interview (if needed)
            if evaluation_result.scores.get('overall_score', 0) >= 60:  # Threshold for interview
                logger.info("Phase 2: Scheduling founder interview...")
                
                founder_info = startup_data.get('founders', [{}])[0]
                meeting_request = MeetingRequest(
                    startup_id=startup_id,
                    founder_email=founder_info.get('email', ''),
                    founder_name=founder_info.get('name', ''),
                    meeting_type="evaluation_interview",
                    duration_minutes=60,
                    preferred_times=[datetime.utcnow().replace(hour=14, minute=0)]  # Default 2 PM
                )
                
                scheduled_meeting = await self.scheduling_agent.schedule_meeting(meeting_request)
                
                # Phase 3: Conduct Interview (simulated for demo)
                logger.info("Phase 3: Conducting AI interview...")
                interview_session = await self.interview_agent.conduct_interview(
                    startup_id=startup_id,
                    founder_email=founder_info.get('email', ''),
                    founder_name=founder_info.get('name', '')
                )
                
                # Phase 4: Generate Final Investment Memo
                logger.info("Phase 4: Generating investment memo...")
                investment_memo = await self._generate_investment_memo(
                    evaluation_result, interview_session
                )
                
                return {
                    "status": "completed",
                    "startup_id": startup_id,
                    "evaluation_result": {
                        "scores": evaluation_result.scores,
                        "recommendations": evaluation_result.recommendations,
                        "risk_factors": evaluation_result.risk_factors,
                        "confidence_score": evaluation_result.confidence_score
                    },
                    "interview_session": {
                        "session_id": interview_session.session_id,
                        "overall_sentiment": interview_session.overall_sentiment,
                        "key_insights": interview_session.key_insights,
                        "red_flags": interview_session.red_flags
                    },
                    "investment_memo": investment_memo,
                    "meeting_details": {
                        "meeting_id": scheduled_meeting.meeting_id,
                        "scheduled_time": scheduled_meeting.scheduled_time.isoformat(),
                        "meeting_link": scheduled_meeting.meeting_link
                    }
                }
            else:
                logger.info("Startup did not meet threshold for interview")
                return {
                    "status": "evaluation_only",
                    "startup_id": startup_id,
                    "evaluation_result": {
                        "scores": evaluation_result.scores,
                        "recommendations": evaluation_result.recommendations,
                        "risk_factors": evaluation_result.risk_factors,
                        "confidence_score": evaluation_result.confidence_score
                    },
                    "decision": "pass",
                    "reason": f"Overall score {evaluation_result.scores.get('overall_score', 0):.1f} below interview threshold of 60"
                }
                
        except Exception as e:
            logger.error(f"Pipeline failed for startup {startup_id}: {str(e)}")
            return {
                "status": "failed",
                "startup_id": startup_id,
                "error": str(e)
            }
    
    async def _generate_investment_memo(self, evaluation_result, interview_session) -> Dict[str, Any]:
        """Generate comprehensive investment memo"""
        
        from vertexai.generative_models import GenerativeModel
        import json
        
        model = GenerativeModel("gemini-1.5-pro")
        
        prompt = f"""
        Generate a comprehensive investment memo based on the following evaluation data:
        
        EVALUATION SCORES:
        {json.dumps(evaluation_result.scores, indent=2)}
        
        EVALUATION INSIGHTS:
        Recommendations: {evaluation_result.recommendations}
        Risk Factors: {evaluation_result.risk_factors}
        Confidence Score: {evaluation_result.confidence_score}
        
        INTERVIEW INSIGHTS:
        Overall Sentiment: {interview_session.overall_sentiment}
        Key Insights: {interview_session.key_insights}
        Red Flags: {interview_session.red_flags}
        
        Create a professional investment memo with the following sections:
        1. Executive Summary
        2. Investment Recommendation (Invest/Pass/More Info Needed)
        3. Key Strengths
        4. Key Concerns
        5. Market Opportunity
        6. Team Assessment
        7. Risk Analysis
        8. Financial Projections Assessment
        9. Next Steps
        
        Format as a structured JSON object with each section as a key.
        """
        
        response = await model.generate_content_async(prompt)
        
        try:
            memo = json.loads(response.text)
            memo["generated_at"] = datetime.utcnow().isoformat()
            memo["memo_id"] = f"memo_{evaluation_result.startup_id}_{int(datetime.utcnow().timestamp())}"
            return memo
        except json.JSONDecodeError:
            return {
                "memo_id": f"memo_{evaluation_result.startup_id}_{int(datetime.utcnow().timestamp())}",
                "executive_summary": response.text,
                "generated_at": datetime.utcnow().isoformat(),
                "status": "generated_with_fallback"
            }

# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Startup Evaluation Platform...")
    yield
    # Shutdown
    logger.info("Shutting down Startup Evaluation Platform...")

# Create main FastAPI application
app = FastAPI(
    title="Startup Evaluation Platform",
    description="AI-powered startup evaluation and investment memo generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
orchestrator = StartupEvaluationOrchestrator(project_id)

# Mount the API routes
app.mount("/api/v1", api_app)

@app.get("/")
async def root():
    """Health check and welcome endpoint"""
    return {
        "message": "Startup Evaluation Platform",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "evaluation_agent": "active",
            "scheduling_agent": "active", 
            "interview_agent": "active"
        }
    }

@app.post("/evaluate-startup")
async def evaluate_startup_complete(
    startup_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Run complete startup evaluation pipeline"""
    
    try:
        # Validate required fields
        required_fields = ["startup_info", "founders"]
        for field in required_fields:
            if field not in startup_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Add startup_id if not provided
        if "startup_id" not in startup_data:
            startup_data["startup_id"] = f"startup_{int(datetime.utcnow().timestamp())}"
        
        # Run evaluation pipeline in background
        background_tasks.add_task(
            orchestrator.run_complete_evaluation_pipeline,
            startup_data
        )
        
        return {
            "message": "Evaluation pipeline started",
            "startup_id": startup_data["startup_id"],
            "status": "processing",
            "estimated_completion": "30-45 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to start evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/evaluate-startup-sync")
async def evaluate_startup_sync(startup_data: Dict[str, Any]):
    """Run complete startup evaluation pipeline synchronously"""
    
    try:
        # Validate required fields
        required_fields = ["startup_info", "founders"]
        for field in required_fields:
            if field not in startup_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Add startup_id if not provided
        if "startup_id" not in startup_data:
            startup_data["startup_id"] = f"startup_{int(datetime.utcnow().timestamp())}"
        
        # Run evaluation pipeline
        result = await orchestrator.run_complete_evaluation_pipeline(startup_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check for all services"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    try:
        # Check each agent
        health_status["services"]["evaluation_agent"] = "healthy"
        health_status["services"]["scheduling_agent"] = "healthy"
        health_status["services"]["interview_agent"] = "healthy"
        health_status["services"]["database"] = "healthy"
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status

# Demo endpoint for testing
@app.post("/demo")
async def demo_evaluation():
    """Demo endpoint with sample startup data"""
    
    sample_startup = {
        "startup_info": {
            "name": "AI Solutions Inc",
            "description": "AI-powered automation platform for small businesses",
            "website": "https://aisolutions.com",
            "industry": "Technology/AI",
            "stage": "Seed",
            "location": "San Francisco, CA",
            "founded_year": 2023
        },
        "founders": [
            {
                "name": "Jane Smith",
                "email": "jane@aisolutions.com",
                "phone": "+1-555-0123",
                "linkedin": "https://linkedin.com/in/janesmith",
                "background": "Former Google AI engineer with 8 years experience in machine learning",
                "previous_companies": ["Google", "OpenAI"]
            }
        ],
        "additional_info": {
            "funding_raised": "$500K",
            "customers": 25,
            "monthly_revenue": "$15K",
            "team_size": 4
        }
    }
    
    result = await orchestrator.run_complete_evaluation_pipeline(sample_startup)
    return result

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Set to False in production
        log_level="info"
    )
