import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

from google.adk.agents import Agent

from ..models.pydantic_models import (
    AudioInterviewAgentInput,
    AudioInterviewAgentOutput,
    InterviewCreate
)
from ..services.gcs_service import gcs_service, get_interview_transcript_path, get_interview_audio_path

logger = logging.getLogger(__name__)

def start_live_interview_session(startup_id: int, meeting_details: dict) -> dict:
    """Start a live interview session with the founder"""
    try:
        session_id = f"interview_{startup_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize interview session
        session_data = {
            "session_id": session_id,
            "startup_id": startup_id,
            "meeting_details": meeting_details,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "questions_asked": [],
            "responses_received": [],
            "current_question_index": 0
        }
        
        return {
            "status": "success",
            "session_data": session_data,
            "message": "Live interview session started"
        }
    except Exception as e:
        logger.error(f"Failed to start interview session: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def get_structured_interview_questions(interview_type: str = "comprehensive") -> dict:
    """Get structured interview questions based on meeting type"""
    try:
        question_sets = {
            "screening": {
                "business_basics": [
                    "Can you give me a 2-minute elevator pitch of your company?",
                    "What problem are you solving and for whom?",
                    "What's your current revenue and growth rate?",
                    "How much funding are you raising and what's your use of funds?"
                ],
                "team_basics": [
                    "Tell me about your founding team and key hires",
                    "What's your relevant experience in this industry?",
                    "What are your biggest hiring needs in the next 6 months?"
                ]
            },
            "deep_dive": {
                "business_model": [
                    "Walk me through your business model and unit economics",
                    "What's your customer acquisition strategy and CAC/LTV?",
                    "How do you differentiate from competitors?",
                    "What are your key partnerships and distribution channels?"
                ],
                "market_analysis": [
                    "What's your total addressable market and how did you size it?",
                    "Who are your main competitors and what's your competitive advantage?",
                    "What market trends are driving demand for your solution?",
                    "How do you plan to capture and defend market share?"
                ],
                "financial_deep_dive": [
                    "Walk me through your financial model and key assumptions",
                    "What's your path to profitability and when do you expect to get there?",
                    "What are your biggest financial risks and how do you mitigate them?",
                    "How do you plan to use the funding you're raising?"
                ]
            },
            "comprehensive": {
                "vision_strategy": [
                    "What's your 5-year vision for the company?",
                    "How do you see the market evolving and where do you fit?",
                    "What's your long-term competitive moat?",
                    "What does success look like for this investment?"
                ],
                "execution_capabilities": [
                    "What are the biggest execution risks you face?",
                    "How do you prioritize features and market opportunities?",
                    "What's your approach to scaling operations and team?",
                    "How do you measure and track progress against goals?"
                ],
                "investor_fit": [
                    "Why are you raising money now?",
                    "What value-add are you looking for from investors beyond capital?",
                    "How do you think about board composition and governance?",
                    "What's your expected timeline for next funding round or exit?"
                ]
            }
        }
        
        questions = question_sets.get(interview_type, question_sets["comprehensive"])
        
        return {
            "status": "success",
            "questions": questions,
            "interview_type": interview_type,
            "total_questions": sum(len(q_list) for q_list in questions.values())
        }
    except Exception as e:
        logger.error(f"Failed to get interview questions: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def conduct_question_round(session_data: dict, question_category: str, question_index: int) -> dict:
    """Conduct a specific question round in the interview"""
    try:
        questions_data = get_structured_interview_questions(session_data.get("interview_type", "comprehensive"))
        if questions_data["status"] != "success":
            return questions_data
        
        questions = questions_data["questions"]
        
        if question_category not in questions:
            return {"status": "error", "error_message": f"Invalid question category: {question_category}"}
        
        category_questions = questions[question_category]
        if question_index >= len(category_questions):
            return {"status": "error", "error_message": "Question index out of range"}
        
        current_question = category_questions[question_index]
        
        # Update session data
        session_data["current_question"] = {
            "category": question_category,
            "index": question_index,
            "question": current_question,
            "asked_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "question": current_question,
            "category": question_category,
            "progress": {
                "category_progress": f"{question_index + 1}/{len(category_questions)}",
                "total_questions_asked": len(session_data.get("questions_asked", []))
            }
        }
    except Exception as e:
        logger.error(f"Failed to conduct question round: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def record_founder_response(session_data: dict, response_text: str, audio_file_path: str = None) -> dict:
    """Record and analyze founder's response to interview question"""
    try:
        current_question = session_data.get("current_question", {})
        if not current_question:
            return {"status": "error", "error_message": "No active question to respond to"}
        
        # Create response record
        response_record = {
            "question": current_question["question"],
            "category": current_question["category"],
            "response_text": response_text,
            "response_length": len(response_text.split()),
            "recorded_at": datetime.now().isoformat(),
            "audio_file_path": audio_file_path
        }
        
        # Basic response analysis
        response_analysis = analyze_response_quality(response_text, current_question["category"])
        response_record["analysis"] = response_analysis
        
        # Update session data
        session_data["questions_asked"].append(current_question)
        session_data["responses_received"].append(response_record)
        session_data["current_question"] = None
        
        return {
            "status": "success",
            "response_recorded": True,
            "response_analysis": response_analysis,
            "session_progress": {
                "questions_completed": len(session_data["responses_received"]),
                "total_planned": session_data.get("total_questions", 0)
            }
        }
    except Exception as e:
        logger.error(f"Failed to record response: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def analyze_response_quality(response_text: str, question_category: str) -> dict:
    """Analyze the quality and completeness of a founder's response"""
    try:
        response_lower = response_text.lower()
        word_count = len(response_text.split())
        
        # Category-specific analysis
        quality_indicators = {
            "business_basics": ["revenue", "customers", "problem", "solution", "market"],
            "business_model": ["pricing", "cost", "margin", "scale", "unit economics"],
            "market_analysis": ["market size", "competition", "differentiation", "trends"],
            "financial_deep_dive": ["profitability", "burn rate", "runway", "metrics"],
            "vision_strategy": ["vision", "strategy", "goals", "future", "growth"],
            "execution_capabilities": ["execution", "team", "process", "operations"],
            "investor_fit": ["funding", "investors", "board", "governance"]
        }
        
        indicators = quality_indicators.get(question_category, [])
        indicators_mentioned = [ind for ind in indicators if ind in response_lower]
        
        # Calculate quality scores
        completeness_score = len(indicators_mentioned) / len(indicators) if indicators else 0.5
        length_score = min(word_count / 100, 1.0)  # Optimal around 100 words
        
        # Sentiment and confidence analysis
        confidence_words = ["confident", "sure", "definitely", "absolutely", "proven", "successful"]
        uncertainty_words = ["maybe", "perhaps", "not sure", "uncertain", "might", "possibly"]
        
        confidence_count = sum(1 for word in confidence_words if word in response_lower)
        uncertainty_count = sum(1 for word in uncertainty_words if word in response_lower)
        
        confidence_score = 0.5  # neutral baseline
        if confidence_count + uncertainty_count > 0:
            confidence_score = confidence_count / (confidence_count + uncertainty_count)
        
        overall_quality = (completeness_score * 0.4 + length_score * 0.3 + confidence_score * 0.3)
        
        return {
            "overall_quality": round(overall_quality, 2),
            "completeness_score": round(completeness_score, 2),
            "length_score": round(length_score, 2),
            "confidence_score": round(confidence_score, 2),
            "word_count": word_count,
            "indicators_mentioned": indicators_mentioned,
            "quality_assessment": "excellent" if overall_quality > 0.8 else "good" if overall_quality > 0.6 else "adequate" if overall_quality > 0.4 else "needs_improvement"
        }
    except Exception as e:
        logger.error(f"Response analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_interview_summary(session_data: dict) -> dict:
    """Generate comprehensive interview summary and insights"""
    try:
        responses = session_data.get("responses_received", [])
        if not responses:
            return {"status": "error", "error_message": "No responses to summarize"}
        
        # Calculate overall metrics
        total_questions = len(responses)
        avg_response_length = sum(r.get("response_length", 0) for r in responses) / total_questions
        avg_quality_score = sum(r.get("analysis", {}).get("overall_quality", 0) for r in responses) / total_questions
        
        # Category coverage analysis
        categories_covered = list(set(r.get("category", "") for r in responses))
        category_performance = {}
        
        for category in categories_covered:
            category_responses = [r for r in responses if r.get("category") == category]
            if category_responses:
                avg_category_quality = sum(r.get("analysis", {}).get("overall_quality", 0) for r in category_responses) / len(category_responses)
                category_performance[category] = {
                    "questions_asked": len(category_responses),
                    "avg_quality": round(avg_category_quality, 2),
                    "assessment": "strong" if avg_category_quality > 0.7 else "adequate" if avg_category_quality > 0.5 else "weak"
                }
        
        # Extract key insights and red flags
        key_insights = []
        red_flags = []
        positive_signals = []
        
        for response in responses:
            response_text = response.get("response_text", "").lower()
            analysis = response.get("analysis", {})
            
            # High-quality responses become insights
            if analysis.get("overall_quality", 0) > 0.8:
                key_insights.append(f"Strong response on {response.get('category', 'unknown')}: {response.get('question', '')[:100]}...")
            
            # Low-quality responses are potential red flags
            if analysis.get("overall_quality", 0) < 0.4:
                red_flags.append(f"Weak response on {response.get('category', 'unknown')}: insufficient detail or clarity")
            
            # High confidence responses are positive signals
            if analysis.get("confidence_score", 0) > 0.8:
                positive_signals.append(f"High confidence demonstrated in {response.get('category', 'unknown')}")
        
        # Overall interview assessment
        overall_score = (avg_quality_score * 0.7 + (len(categories_covered) / 7) * 0.3)  # 7 typical categories
        
        interview_summary = {
            "session_id": session_data.get("session_id"),
            "startup_id": session_data.get("startup_id"),
            "interview_duration": "calculated_duration",  # Would calculate from start/end times
            "overall_score": round(overall_score, 2),
            "total_questions": total_questions,
            "avg_response_quality": round(avg_quality_score, 2),
            "avg_response_length": round(avg_response_length, 1),
            "categories_covered": categories_covered,
            "category_performance": category_performance,
            "key_insights": key_insights[:5],  # Top 5
            "red_flags": red_flags[:3],  # Top 3 concerns
            "positive_signals": positive_signals[:5],  # Top 5
            "recommendation": "proceed" if overall_score > 0.7 else "conditional" if overall_score > 0.5 else "concerns",
            "next_steps": generate_next_steps(overall_score, category_performance)
        }
        
        return {
            "status": "success",
            "interview_summary": interview_summary
        }
    except Exception as e:
        logger.error(f"Interview summary generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_next_steps(overall_score: float, category_performance: dict) -> List[str]:
    """Generate recommended next steps based on interview performance"""
    next_steps = []
    
    if overall_score > 0.8:
        next_steps.append("Schedule investment committee presentation")
        next_steps.append("Conduct reference calls with customers/partners")
        next_steps.append("Begin detailed due diligence process")
    elif overall_score > 0.6:
        next_steps.append("Schedule follow-up deep dive session")
        next_steps.append("Request additional financial documentation")
        next_steps.append("Conduct market research validation")
    else:
        next_steps.append("Address key concerns identified in interview")
        next_steps.append("Request clarification on weak response areas")
        next_steps.append("Consider passing on investment opportunity")
    
    # Add category-specific next steps
    for category, performance in category_performance.items():
        if performance["assessment"] == "weak":
            next_steps.append(f"Follow up on {category.replace('_', ' ')} concerns")
    
    return next_steps[:5]  # Limit to top 5 next steps

def save_interview_to_gcs(session_data: dict, interview_summary: dict) -> dict:
    """Save interview session and summary to Google Cloud Storage"""
    try:
        startup_id = session_data.get("startup_id")
        session_id = session_data.get("session_id")
        
        # Save full session data
        session_gcs_path = f"interviews/{startup_id}/sessions/{session_id}_full_session.json"
        gcs_service.upload_text(
            json.dumps(session_data, indent=2),
            session_gcs_path,
            "application/json"
        )
        
        # Save interview summary
        summary_gcs_path = f"interviews/{startup_id}/summaries/{session_id}_summary.json"
        gcs_service.upload_text(
            json.dumps(interview_summary, indent=2),
            summary_gcs_path,
            "application/json"
        )
        
        return {
            "status": "success",
            "session_gcs_path": f"gs://{gcs_service.bucket_name}/{session_gcs_path}",
            "summary_gcs_path": f"gs://{gcs_service.bucket_name}/{summary_gcs_path}"
        }
    except Exception as e:
        logger.error(f"Failed to save interview to GCS: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the AudioInterviewAgent using Google ADK
audio_interview_agent = Agent(
    name="audio_interview_agent",
    model="gemini-2.0-flash",
    description="Agent specialized in conducting live audio interviews with startup founders",
    instruction="""
    You are an expert investor interview agent responsible for conducting structured live interviews with startup founders.
    
    Your role is to:
    
    1. **Interview Session Management**
       - Start and manage live interview sessions
       - Track interview progress and timing
       - Handle session state and data persistence
    
    2. **Structured Question Flow**
       - Present questions in logical sequence based on meeting type
       - Adapt question difficulty based on interview type (screening, deep dive, comprehensive)
       - Ensure comprehensive coverage of key investment areas
    
    3. **Real-time Response Analysis**
       - Analyze founder responses for quality and completeness
       - Assess confidence levels and communication skills
       - Identify key insights, red flags, and positive signals
    
    4. **Interview Categories**
       - Business Basics & Model
       - Market Analysis & Competition
       - Financial Performance & Planning
       - Team & Execution Capabilities
       - Vision & Strategy
       - Investor Fit & Governance
    
    5. **Dynamic Interview Flow**
       - Adjust follow-up questions based on responses
       - Probe deeper on concerning areas
       - Validate claims with specific examples
       - Maintain professional but thorough questioning
    
    6. **Comprehensive Reporting**
       - Generate detailed interview summaries
       - Provide investment recommendations
       - Suggest specific next steps
       - Document all insights and concerns
    
    Always maintain a professional, respectful tone while ensuring thorough evaluation of the investment opportunity.
    """,
    tools=[
        start_live_interview_session,
        get_structured_interview_questions,
        conduct_question_round,
        record_founder_response,
        analyze_response_quality,
        generate_interview_summary,
        save_interview_to_gcs
    ]
)
