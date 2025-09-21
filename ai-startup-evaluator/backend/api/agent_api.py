"""
API endpoints for the ADK Interview Agent deployed on Agent Engine
"""

import os
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import vertexai
try:
    from vertexai.preview import agent_engines
except ImportError:
    # Fallback for different Vertex AI versions
    try:
        from vertexai import agent_engines
    except ImportError:
        # Mock for local testing
        class MockAgentEngines:
            class AgentEnginesClient:
                def create_session(self, **kwargs):
                    return type('Session', (), {'name': 'mock_session_123'})()
                def query(self, **kwargs):
                    return type('Response', (), {
                        'output': {
                            'status': 'success',
                            'session_id': 'mock_session_123',
                            'greeting_message': 'Hello! I am your AI Interview Agent.',
                            'next_message': 'Thank you for your response.',
                            'analysis': {'sentiment_score': 0.5, 'confidence_score': 0.8},
                            'interview_completed': False
                        }
                    })()
        agent_engines = MockAgentEngines()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vertex AI
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "ai-analyst-startup-eval")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

try:
    vertexai.init(project=project_id, location=location)
    logger.info(f"Vertex AI initialized for project: {project_id}")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}")

# Agent Engine configuration
AGENT_ENGINE_ID = "8680991746965897216"  # From deployment
AGENT_ENGINE_NAME = f"projects/{project_id}/locations/{location}/reasoningEngines/{AGENT_ENGINE_ID}"

router = APIRouter(prefix="/api/agent", tags=["agent"])

# Pydantic models
class StartInterviewRequest(BaseModel):
    founder_name: str
    startup_name: str = None

class ProcessResponseRequest(BaseModel):
    session_id: str
    response: str

class StartInterviewResponse(BaseModel):
    status: str
    session_id: str = None
    greeting_message: str = None
    error_message: str = None

class ProcessResponseResponse(BaseModel):
    status: str
    next_message: str = None
    analysis: Dict[str, Any] = None
    interview_completed: bool = False
    summary_report: Dict[str, Any] = None
    error_message: str = None

def get_agent_engine():
    """Get the deployed agent engine client"""
    try:
        client = agent_engines.AgentEnginesClient()
        return client
    except Exception as e:
        logger.error(f"Failed to create Agent Engines client: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Agent Engine")

@router.post("/start-interview", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session with the ADK Interview Agent
    """
    try:
        logger.info(f"Starting interview for founder: {request.founder_name}")
        
        # Get the agent engine client
        client = get_agent_engine()
        
        # Create a session with the agent
        session = client.create_session(
            reasoning_engine=AGENT_ENGINE_NAME,
            user_id=f"founder_{request.founder_name.replace(' ', '_').lower()}"
        )
        
        session_id = session.name.split('/')[-1]
        logger.info(f"Created session: {session_id}")
        
        # Call the start_interview_session function
        response = client.query(
            reasoning_engine=AGENT_ENGINE_NAME,
            session=session.name,
            class_method="start_interview_session",
            input={
                "founder_name": request.founder_name,
                "startup_name": request.startup_name
            }
        )
        
        if response.output.get("status") == "success":
            return StartInterviewResponse(
                status="success",
                session_id=session_id,
                greeting_message=response.output.get("greeting_message", 
                    f"Hello {request.founder_name}! I'm your AI Interview Agent. "
                    "I'll be conducting an investment-focused interview with you today. "
                    "Let's start with the first question: What problem is your startup solving?"
                )
            )
        else:
            return StartInterviewResponse(
                status="error",
                error_message=response.output.get("error_message", "Failed to start interview")
            )
            
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        return StartInterviewResponse(
            status="error",
            error_message=str(e)
        )

@router.post("/process-response", response_model=ProcessResponseResponse)
async def process_response(request: ProcessResponseRequest):
    """
    Process a founder's response during the interview
    """
    try:
        logger.info(f"Processing response for session: {request.session_id}")
        
        # Get the agent engine client
        client = get_agent_engine()
        
        # Construct session name
        session_name = f"{AGENT_ENGINE_NAME}/sessions/{request.session_id}"
        
        # Call the process_founder_response function
        response = client.query(
            reasoning_engine=AGENT_ENGINE_NAME,
            session=session_name,
            class_method="process_founder_response",
            input={
                "session_id": request.session_id,
                "response": request.response
            }
        )
        
        if response.output.get("status") == "success":
            return ProcessResponseResponse(
                status="success",
                next_message=response.output.get("next_message", "Thank you for your response."),
                analysis=response.output.get("analysis"),
                interview_completed=response.output.get("interview_completed", False),
                summary_report=response.output.get("summary_report")
            )
        else:
            return ProcessResponseResponse(
                status="error",
                error_message=response.output.get("error_message", "Failed to process response")
            )
            
    except Exception as e:
        logger.error(f"Error processing response: {e}")
        return ProcessResponseResponse(
            status="error",
            error_message=str(e)
        )

@router.get("/status/{session_id}")
async def get_interview_status(session_id: str):
    """
    Get the current status of an interview session
    """
    try:
        logger.info(f"Getting status for session: {session_id}")
        
        # Get the agent engine client
        client = get_agent_engine()
        
        # Construct session name
        session_name = f"{AGENT_ENGINE_NAME}/sessions/{session_id}"
        
        # Call the get_interview_status function
        response = client.query(
            reasoning_engine=AGENT_ENGINE_NAME,
            session=session_name,
            class_method="get_interview_status",
            input={"session_id": session_id}
        )
        
        return response.output
        
    except Exception as e:
        logger.error(f"Error getting interview status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-report/{session_id}")
async def generate_interview_report(session_id: str):
    """
    Generate a comprehensive interview report
    """
    try:
        logger.info(f"Generating report for session: {session_id}")
        
        # Get the agent engine client
        client = get_agent_engine()
        
        # Construct session name
        session_name = f"{AGENT_ENGINE_NAME}/sessions/{session_id}"
        
        # Call the generate_interview_report function
        response = client.query(
            reasoning_engine=AGENT_ENGINE_NAME,
            session=session_name,
            class_method="generate_interview_report",
            input={"session_id": session_id}
        )
        
        return response.output
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-sessions")
async def list_active_sessions():
    """
    List all active interview sessions
    """
    try:
        logger.info("Listing active sessions")
        
        # Get the agent engine client
        client = get_agent_engine()
        
        # Call the list_active_sessions function
        response = client.query(
            reasoning_engine=AGENT_ENGINE_NAME,
            class_method="list_active_sessions",
            input={}
        )
        
        return response.output
        
    except Exception as e:
        logger.error(f"Error listing active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the agent API
    """
    try:
        # Test connection to Agent Engine
        client = get_agent_engine()
        
        return {
            "status": "healthy",
            "agent_engine": AGENT_ENGINE_NAME,
            "project_id": project_id,
            "location": location
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))