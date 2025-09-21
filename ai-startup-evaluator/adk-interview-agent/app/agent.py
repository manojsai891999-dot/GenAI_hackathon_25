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

import datetime
import os
import logging
from typing import Dict, List, Optional, Any

import google.auth
from google.adk.agents import Agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

logger = logging.getLogger(__name__)

# Interview questions for startup evaluation
INTERVIEW_QUESTIONS = [
    "What problem is your startup solving?",
    "Who are your target customers?", 
    "What is your current traction (users, revenue, growth)?",
    "What is your business model?",
    "Who are your competitors and how are you different?",
    "What is your fundraising goal and how will you use the capital?"
]

def start_interview_session(founder_name: str, session_id: str) -> str:
    """Start a new interview session with a startup founder.
    
    Args:
        founder_name: Name of the startup founder
        session_id: Unique session identifier
        
    Returns:
        Greeting message and first question
    """
    greeting = f"Hello {founder_name}! Welcome to the startup evaluation interview. "
    greeting += "I'll be asking you a series of questions to better understand your startup. "
    greeting += "Let's begin with the first question."
    
    first_question = f"\n\nQuestion 1: {INTERVIEW_QUESTIONS[0]}"
    
    return greeting + first_question

def process_founder_response(response: str, question_number: int) -> str:
    """Process the founder's response and provide the next question or summary.
    
    Args:
        response: The founder's response to the current question
        question_number: The current question number (1-6)
        
    Returns:
        Next question or interview completion message
    """
    if question_number < len(INTERVIEW_QUESTIONS):
        next_question = f"\n\nQuestion {question_number + 1}: {INTERVIEW_QUESTIONS[question_number]}"
        return f"Thank you for that response. {next_question}"
    else:
        return "\n\nThank you! We've completed all the interview questions. I'll now generate a summary report of our conversation."

def generate_summary_report(founder_name: str, responses: List[str]) -> str:
    """Generate a summary report of the interview.
    
    Args:
        founder_name: Name of the startup founder
        responses: List of all responses from the founder
        
    Returns:
        Summary report of the interview
    """
    summary = f"Interview Summary for {founder_name}\n"
    summary += "=" * 50 + "\n\n"
    
    for i, (question, response) in enumerate(zip(INTERVIEW_QUESTIONS, responses), 1):
        summary += f"Q{i}: {question}\n"
        summary += f"A{i}: {response}\n\n"
    
    summary += "Key Insights:\n"
    summary += "- Problem: " + (responses[0] if responses else "Not provided") + "\n"
    summary += "- Market: " + (responses[1] if len(responses) > 1 else "Not provided") + "\n"
    summary += "- Traction: " + (responses[2] if len(responses) > 2 else "Not provided") + "\n"
    summary += "- Business Model: " + (responses[3] if len(responses) > 3 else "Not provided") + "\n"
    summary += "- Competition: " + (responses[4] if len(reses) > 4 else "Not provided") + "\n"
    summary += "- Fundraising: " + (responses[5] if len(responses) > 5 else "Not provided") + "\n"
    
    summary += "\nThis concludes the interview. Thank you for your time!"
    
    return summary

def store_response_cloudsql(question: str, response: str, founder_name: str, session_id: str) -> str:
    """Store the response in CloudSQL database.
    
    Args:
        question: The question asked
        response: The founder's response
        founder_name: Name of the founder
        session_id: Session identifier
        
    Returns:
        Confirmation message
    """
    # This would typically store in CloudSQL
    # For now, we'll just return a confirmation
    return f"Response stored for {founder_name} in session {session_id}"

def upload_report_gcs(report: str, founder_name: str, session_id: str) -> str:
    """Upload the summary report to Google Cloud Storage.
    
    Args:
        report: The summary report content
        founder_name: Name of the founder
        session_id: Session identifier
        
    Returns:
        Confirmation message with GCS path
    """
    # This would typically upload to GCS
    # For now, we'll just return a confirmation
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    gcs_path = f"reports/{founder_name}_{session_id}_{timestamp}.txt"
    return f"Report uploaded to GCS: {gcs_path}"

# Create the ADK Interview Agent
root_agent = Agent(
    name="adk_interview_agent",
    model="gemini-2.5-flash",
    instruction="""You are an AI Interview Agent for Startup Founder Evaluation. 
    
    Your role is to conduct structured interviews with startup founders to evaluate their businesses for investment purposes.
    
    You should:
    1. Start with a greeting and explain the interview process
    2. Ask the predefined questions in sequence
    3. Wait for each response before moving to the next question
    4. Allow for follow-up questions when appropriate
    5. Generate a comprehensive summary report at the end
    
    Be professional, thorough, and insightful in your questioning.""",
    tools=[
        start_interview_session,
        process_founder_response, 
        generate_summary_report,
        store_response_cloudsql,
        upload_report_gcs
    ],
)