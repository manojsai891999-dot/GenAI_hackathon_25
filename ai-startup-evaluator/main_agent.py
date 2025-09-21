#!/usr/bin/env python3
"""
Main ADK Interview Agent for Agent Engine Deployment
This is the entry point for the deployed agent on Google Cloud Agent Engine
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from google.adk import Agent, memory, sessions
    from google.adk.memory import Memory
    from google.adk.sessions import Session as ADKSession
except ImportError:
    # Fallback for local testing
    print("Warning: Google ADK not available, using mock classes for local testing")
    class Agent:
        def __init__(self, **kwargs):
            self.name = kwargs.get('name', 'mock_agent')
            self.description = kwargs.get('description', 'Mock agent')
            self.tools = kwargs.get('tools', [])
    
    class Memory:
        def store(self, data):
            pass
        def retrieve(self, query):
            return None
        def retrieve_all(self):
            return []
    
    class ADKSession:
        def __init__(self, **kwargs):
            self.session_id = kwargs.get('session_id')
            self.user_id = kwargs.get('user_id')
            self.context = kwargs.get('context', {})

# Import our interview agent components
from backend.agents.adk_interview_agent import interview_agent
from backend.models.database import create_tables
from backend.services.gcs_service import gcs_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize memory for the agent
agent_memory = Memory()

# Create database tables on startup
try:
    create_tables()
    logger.info("Database tables initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

def start_interview_session(founder_name: str, startup_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a new interview session with a founder
    
    Args:
        founder_name: Name of the founder being interviewed
        startup_name: Name of the startup (optional)
    
    Returns:
        Dictionary containing session details and greeting message
    """
    try:
        logger.info(f"Starting interview session for {founder_name} at {startup_name}")
        
        # Use the interview agent to start the session
        result = interview_agent.start_interview_session(founder_name, startup_name)
        
        if result["status"] == "success":
            # Store session info in agent memory
            agent_memory.store({
                "session_id": result["session_id"],
                "founder_name": founder_name,
                "startup_name": startup_name,
                "start_time": datetime.now().isoformat(),
                "status": "active"
            })
            
            logger.info(f"Interview session started successfully: {result['session_id']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to start interview session: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def process_founder_response(session_id: str, response: str) -> Dict[str, Any]:
    """
    Process a founder's response during the interview
    
    Args:
        session_id: ID of the interview session
        response: The founder's response text
    
    Returns:
        Dictionary containing the next question and analysis
    """
    try:
        logger.info(f"Processing response for session {session_id}")
        
        # Retrieve session data from memory
        session_data = agent_memory.retrieve({"session_id": session_id})
        if not session_data:
            return {
                "status": "error",
                "error_message": "Session not found"
            }
        
        # Create session data structure for the interview agent
        session_info = {
            "session_id": session_id,
            "founder_name": session_data.get("founder_name", "Unknown"),
            "startup_name": session_data.get("startup_name")
        }
        
        # Process the response using the interview agent
        result = interview_agent.process_founder_response(session_info, response)
        
        if result["status"] == "success":
            # Update memory with progress
            agent_memory.store({
                "session_id": session_id,
                "last_response_time": datetime.now().isoformat(),
                "questions_answered": result["progress"]["questions_answered"],
                "progress_percentage": result["progress"]["progress_percentage"]
            })
            
            logger.info(f"Response processed successfully for session {session_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to process founder response: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def get_interview_status(session_id: str) -> Dict[str, Any]:
    """
    Get the current status of an interview session
    
    Args:
        session_id: ID of the interview session
    
    Returns:
        Dictionary containing session status information
    """
    try:
        session_data = agent_memory.retrieve({"session_id": session_id})
        
        if not session_data:
            return {
                "status": "error",
                "error_message": "Session not found"
            }
        
        return {
            "status": "success",
            "session_data": session_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get interview status: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def generate_interview_report(session_id: str) -> Dict[str, Any]:
    """
    Generate a comprehensive interview report
    
    Args:
        session_id: ID of the interview session
    
    Returns:
        Dictionary containing the generated report
    """
    try:
        logger.info(f"Generating interview report for session {session_id}")
        
        # Retrieve session data
        session_data = agent_memory.retrieve({"session_id": session_id})
        if not session_data:
            return {
                "status": "error",
                "error_message": "Session not found"
            }
        
        # Create session info for the interview agent
        session_info = {
            "session_id": session_id,
            "founder_name": session_data.get("founder_name", "Unknown"),
            "startup_name": session_data.get("startup_name")
        }
        
        # Generate the report using the interview agent
        # This will trigger the completion process and generate the summary
        result = interview_agent.process_founder_response(
            session_info, 
            "Generate final report"
        )
        
        if result.get("interview_completed"):
            return {
                "status": "success",
                "report": result.get("summary_report", {}),
                "gcs_path": result.get("gcs_path", ""),
                "completion_message": result.get("completion_message", "")
            }
        else:
            return {
                "status": "error",
                "error_message": "Interview not completed yet"
            }
        
    except Exception as e:
        logger.error(f"Failed to generate interview report: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

def list_active_sessions() -> Dict[str, Any]:
    """
    List all active interview sessions
    
    Returns:
        Dictionary containing list of active sessions
    """
    try:
        # Get all sessions from memory
        all_sessions = agent_memory.retrieve_all()
        
        active_sessions = [
            session for session in all_sessions 
            if session.get("status") == "active"
        ]
        
        return {
            "status": "success",
            "active_sessions": active_sessions,
            "count": len(active_sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to list active sessions: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

# Create the main ADK Agent
adk_interview_agent = Agent(
    name="adk_interview_agent",
    model="gemini-2.0-flash",
    description="AI Interview Agent for Startup Founder Evaluation with CloudSQL + GCS Integration",
    instruction="""
    You are an expert AI interviewer conducting investment-focused interviews with startup founders.
    
    Your capabilities include:
    1. Starting interview sessions with founders
    2. Processing founder responses with real-time analysis
    3. Asking follow-up questions based on response quality
    4. Generating comprehensive investment evaluation reports
    5. Storing all data in CloudSQL and reports in GCS
    
    You maintain a professional yet friendly tone and provide detailed analysis of each response
    including sentiment analysis, confidence scoring, and identification of key insights, risks,
    and positive signals.
    
    Use the available tools to conduct thorough investment evaluations.
    """,
    tools=[
        start_interview_session,
        process_founder_response,
        get_interview_status,
        generate_interview_report,
        list_active_sessions
    ]
)

# Export the agent for deployment
__all__ = ["adk_interview_agent"]