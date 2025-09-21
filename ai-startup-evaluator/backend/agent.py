# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import google.auth
from google.adk import Agent

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Set up environment variables
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our interview agent components
from agents.adk_interview_agent import interview_agent
from models.database import create_tables

# Create database tables on startup (only if not in production)
if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    try:
        # Use SQLite for local testing
        os.environ["DATABASE_URL"] = "sqlite:///./test_startup_evaluator.db"
        create_tables()
        logger.info("Database tables initialized successfully (SQLite)")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
else:
    logger.info("Skipping database initialization in production - will be handled by CloudSQL")

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
        
        # Create session data structure for the interview agent
        session_info = {
            "session_id": session_id,
            "founder_name": "Unknown",  # Will be retrieved from database
            "startup_name": None
        }
        
        # Process the response using the interview agent
        result = interview_agent.process_founder_response(session_info, response)
        
        if result["status"] == "success":
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
        # This would typically query the database for session status
        return {
            "status": "success",
            "session_id": session_id,
            "message": "Session status retrieved"
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
        
        # Create session info for the interview agent
        session_info = {
            "session_id": session_id,
            "founder_name": "Unknown",
            "startup_name": None
        }
        
        # Generate the report using the interview agent
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
        # This would typically query the database for active sessions
        return {
            "status": "success",
            "active_sessions": [],
            "count": 0
        }
        
    except Exception as e:
        logger.error(f"Failed to list active sessions: {e}")
        return {
            "status": "error",
            "error_message": str(e)
        }

# Create the main ADK Agent
root_agent = Agent(
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
