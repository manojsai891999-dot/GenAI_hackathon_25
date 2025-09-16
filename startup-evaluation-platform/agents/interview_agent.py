"""
Interview Agent - Python Implementation
AI agent for conducting voice interviews with startup founders
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

from google.cloud import firestore
from google.cloud import speech
from google.cloud import texttospeech
from google.cloud import storage
from vertexai.generative_models import GenerativeModel
import vertexai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterviewStatus(Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InterviewSection(Enum):
    INTRODUCTION = "introduction"
    FOUNDER_BACKGROUND = "founder_background"
    PROBLEM_DEEP_DIVE = "problem_deep_dive"
    SOLUTION_VALIDATION = "solution_validation"
    TEAM_DYNAMICS = "team_dynamics"
    BUSINESS_MODEL = "business_model"
    WRAP_UP = "wrap_up"

@dataclass
class InterviewQuestion:
    section: InterviewSection
    question: str
    follow_up_triggers: List[str]
    importance: int  # 1-5 scale

@dataclass
class InterviewResponse:
    question: str
    response: str
    timestamp: datetime
    sentiment_score: float
    confidence_score: float
    red_flags: List[str]

@dataclass
class InterviewSession:
    session_id: str
    startup_id: str
    founder_name: str
    founder_email: str
    status: InterviewStatus
    start_time: datetime
    end_time: Optional[datetime]
    responses: List[InterviewResponse]
    overall_sentiment: float
    key_insights: List[str]
    red_flags: List[str]

class StartupInterviewAgent:
    """AI agent for conducting structured interviews with startup founders"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        
        # Initialize Google Cloud services
        self.db = firestore.Client()
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.storage_client = storage.Client()
        
        # Interview configuration
        self.interview_structure = self._initialize_interview_structure()
        self.current_section = InterviewSection.INTRODUCTION
        self.section_start_time = None
        
        # Voice configuration
        self.voice_config = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
    
    def _initialize_interview_structure(self) -> Dict[InterviewSection, Dict[str, Any]]:
        """Initialize the structured interview framework"""
        
        return {
            InterviewSection.INTRODUCTION: {
                "duration": 300,  # 5 minutes
                "objectives": ["establish_rapport", "explain_process", "get_consent"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.INTRODUCTION,
                        question="Thank you for joining us today. Before we begin, may I have your consent to record this conversation for evaluation purposes?",
                        follow_up_triggers=["consent", "recording"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.INTRODUCTION,
                        question="Could you briefly introduce yourself and your role at the company?",
                        follow_up_triggers=["background", "role"],
                        importance=4
                    )
                ]
            },
            
            InterviewSection.FOUNDER_BACKGROUND: {
                "duration": 900,  # 15 minutes
                "objectives": ["assess_experience", "understand_motivation", "evaluate_domain_expertise"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.FOUNDER_BACKGROUND,
                        question="Tell me about your journey that led to starting this company. What specific experiences prepared you for this venture?",
                        follow_up_triggers=["vague", "generic", "missing_details"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.FOUNDER_BACKGROUND,
                        question="What specific experience do you have in this market or industry?",
                        follow_up_triggers=["no_experience", "limited_experience"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.FOUNDER_BACKGROUND,
                        question="How did you first identify this problem? Was it through personal experience or market research?",
                        follow_up_triggers=["personal_experience", "market_research", "timing"],
                        importance=4
                    )
                ]
            },
            
            InterviewSection.PROBLEM_DEEP_DIVE: {
                "duration": 900,  # 15 minutes
                "objectives": ["validate_problem", "understand_market", "assess_urgency"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.PROBLEM_DEEP_DIVE,
                        question="Walk me through the exact problem you're solving. Can you give me a specific example of how this problem manifests for your customers?",
                        follow_up_triggers=["vague_problem", "no_examples", "theoretical"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.PROBLEM_DEEP_DIVE,
                        question="How are customers currently handling this problem? What's the cost of not solving it?",
                        follow_up_triggers=["no_current_solution", "cost_unclear"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.PROBLEM_DEEP_DIVE,
                        question="How big is this market? Have you validated the market size through research or customer interviews?",
                        follow_up_triggers=["no_validation", "unrealistic_size"],
                        importance=4
                    )
                ]
            },
            
            InterviewSection.SOLUTION_VALIDATION: {
                "duration": 900,  # 15 minutes
                "objectives": ["assess_solution_fit", "understand_validation", "evaluate_traction"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.SOLUTION_VALIDATION,
                        question="How does your solution uniquely address this problem? What makes it different from existing alternatives?",
                        follow_up_triggers=["not_unique", "unclear_differentiation"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.SOLUTION_VALIDATION,
                        question="What validation have you done with actual customers? Can you share specific feedback or metrics?",
                        follow_up_triggers=["no_validation", "vague_metrics", "no_customers"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.SOLUTION_VALIDATION,
                        question="What's your current traction? How many customers do you have and what's your growth rate?",
                        follow_up_triggers=["no_traction", "declining_growth", "unrealistic_projections"],
                        importance=4
                    )
                ]
            },
            
            InterviewSection.TEAM_DYNAMICS: {
                "duration": 600,  # 10 minutes
                "objectives": ["assess_team_strength", "understand_dynamics", "identify_gaps"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.TEAM_DYNAMICS,
                        question="Tell me about your co-founders and key team members. What unique skills does each person bring?",
                        follow_up_triggers=["weak_team", "missing_skills", "no_cofounders"],
                        importance=4
                    ),
                    InterviewQuestion(
                        section=InterviewSection.TEAM_DYNAMICS,
                        question="How do you handle disagreements or conflicts within the team? Can you give me an example?",
                        follow_up_triggers=["poor_communication", "unresolved_conflicts"],
                        importance=3
                    ),
                    InterviewQuestion(
                        section=InterviewSection.TEAM_DYNAMICS,
                        question="What are the biggest skill gaps you need to fill in the next 12 months?",
                        follow_up_triggers=["no_awareness", "critical_gaps"],
                        importance=3
                    )
                ]
            },
            
            InterviewSection.BUSINESS_MODEL: {
                "duration": 900,  # 15 minutes
                "objectives": ["understand_monetization", "assess_scalability", "evaluate_metrics"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.BUSINESS_MODEL,
                        question="How do you make money? Walk me through your revenue model and pricing strategy.",
                        follow_up_triggers=["unclear_model", "no_revenue", "unsustainable_pricing"],
                        importance=5
                    ),
                    InterviewQuestion(
                        section=InterviewSection.BUSINESS_MODEL,
                        question="What's your path to profitability? When do you expect to break even?",
                        follow_up_triggers=["no_path", "unrealistic_timeline"],
                        importance=4
                    ),
                    InterviewQuestion(
                        section=InterviewSection.BUSINESS_MODEL,
                        question="What are your key metrics and how are you currently performing against them?",
                        follow_up_triggers=["wrong_metrics", "poor_performance", "no_tracking"],
                        importance=4
                    )
                ]
            },
            
            InterviewSection.WRAP_UP: {
                "duration": 300,  # 5 minutes
                "objectives": ["summarize_key_points", "clarify_next_steps", "thank_participant"],
                "questions": [
                    InterviewQuestion(
                        section=InterviewSection.WRAP_UP,
                        question="Is there anything important about your startup that we haven't covered today?",
                        follow_up_triggers=["new_information"],
                        importance=3
                    ),
                    InterviewQuestion(
                        section=InterviewSection.WRAP_UP,
                        question="What questions do you have about our investment process or evaluation criteria?",
                        follow_up_triggers=["process_questions"],
                        importance=2
                    )
                ]
            }
        }
    
    async def conduct_interview(self, startup_id: str, founder_email: str, founder_name: str) -> InterviewSession:
        """Conduct a complete interview session"""
        
        session_id = str(uuid.uuid4())
        logger.info(f"Starting interview session {session_id} with {founder_name}")
        
        session = InterviewSession(
            session_id=session_id,
            startup_id=startup_id,
            founder_name=founder_name,
            founder_email=founder_email,
            status=InterviewStatus.IN_PROGRESS,
            start_time=datetime.utcnow(),
            end_time=None,
            responses=[],
            overall_sentiment=0.0,
            key_insights=[],
            red_flags=[]
        )
        
        try:
            # Save initial session
            await self._save_session(session)
            
            # Conduct each section of the interview
            for section in InterviewSection:
                logger.info(f"Starting section: {section.value}")
                self.current_section = section
                self.section_start_time = datetime.utcnow()
                
                section_responses = await self._conduct_section(session, section)
                session.responses.extend(section_responses)
                
                # Update session after each section
                await self._save_session(session)
            
            # Finalize interview
            session.status = InterviewStatus.COMPLETED
            session.end_time = datetime.utcnow()
            
            # Generate final analysis
            session.overall_sentiment = await self._calculate_overall_sentiment(session.responses)
            session.key_insights = await self._extract_key_insights(session.responses)
            session.red_flags = await self._identify_red_flags(session.responses)
            
            # Save final session
            await self._save_session(session)
            
            # Generate interview report
            await self._generate_interview_report(session)
            
            logger.info(f"Interview completed successfully: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Interview failed: {str(e)}")
            session.status = InterviewStatus.CANCELLED
            await self._save_session(session)
            raise
    
    async def _conduct_section(self, session: InterviewSession, section: InterviewSection) -> List[InterviewResponse]:
        """Conduct a specific section of the interview"""
        
        section_config = self.interview_structure[section]
        questions = section_config["questions"]
        responses = []
        
        for question_obj in questions:
            # Ask the question
            response_text = await self._ask_question_and_get_response(question_obj.question)
            
            # Analyze the response
            analysis = await self._analyze_response(question_obj.question, response_text)
            
            response = InterviewResponse(
                question=question_obj.question,
                response=response_text,
                timestamp=datetime.utcnow(),
                sentiment_score=analysis["sentiment_score"],
                confidence_score=analysis["confidence_score"],
                red_flags=analysis["red_flags"]
            )
            
            responses.append(response)
            
            # Generate follow-up questions if needed
            if analysis["needs_followup"]:
                followup_questions = await self._generate_followup_questions(
                    question_obj, response_text, analysis
                )
                
                for followup in followup_questions:
                    followup_response = await self._ask_question_and_get_response(followup)
                    followup_analysis = await self._analyze_response(followup, followup_response)
                    
                    responses.append(InterviewResponse(
                        question=followup,
                        response=followup_response,
                        timestamp=datetime.utcnow(),
                        sentiment_score=followup_analysis["sentiment_score"],
                        confidence_score=followup_analysis["confidence_score"],
                        red_flags=followup_analysis["red_flags"]
                    ))
        
        return responses
    
    async def _ask_question_and_get_response(self, question: str) -> str:
        """Ask a question using text-to-speech and get response via speech-to-text"""
        
        # Convert question to speech
        await self._speak_text(question)
        
        # Listen for response (placeholder - implement actual speech recognition)
        response = await self._listen_for_response()
        
        return response
    
    async def _speak_text(self, text: str):
        """Convert text to speech and play it"""
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=self.voice_config,
            audio_config=self.audio_config
        )
        
        # In a real implementation, you would play this audio
        # For now, we'll just log that the question was asked
        logger.info(f"Asked question: {text[:50]}...")
    
    async def _listen_for_response(self) -> str:
        """Listen for and transcribe the founder's response"""
        
        # This is a placeholder implementation
        # In a real system, you would:
        # 1. Record audio from microphone
        # 2. Send to Speech-to-Text API
        # 3. Return transcribed text
        
        # For demo purposes, return a sample response
        sample_responses = [
            "Well, I started this company because I experienced this problem firsthand when I was working at my previous job. We were constantly struggling with inefficient processes.",
            "Our solution is unique because we use AI to automate what was previously a manual process. This saves our customers about 40% of their time.",
            "We've validated this with 50 potential customers through interviews, and 80% said they would pay for this solution.",
            "Our team has complementary skills - I handle the business side while my co-founder is the technical lead with 15 years of experience."
        ]
        
        import random
        return random.choice(sample_responses)
    
    async def _analyze_response(self, question: str, response: str) -> Dict[str, Any]:
        """Analyze the founder's response using AI"""
        
        prompt = f"""
        Analyze this interview response for quality and content:
        
        Question: {question}
        Response: {response}
        
        Evaluate:
        1. Sentiment score (-1 to 1)
        2. Confidence score (0 to 1) - how confident/clear is the response
        3. Completeness (0 to 1) - how well does it answer the question
        4. Red flags (list any concerning elements)
        5. Whether follow-up questions are needed
        
        Return as JSON:
        {{
            "sentiment_score": 0.5,
            "confidence_score": 0.8,
            "completeness": 0.7,
            "red_flags": ["vague response", "no specific examples"],
            "needs_followup": true,
            "key_points": ["point1", "point2"]
        }}
        """
        
        ai_response = await self.model.generate_content_async(prompt)
        
        try:
            analysis = json.loads(ai_response.text)
            return analysis
        except json.JSONDecodeError:
            # Return default analysis if parsing fails
            return {
                "sentiment_score": 0.0,
                "confidence_score": 0.5,
                "completeness": 0.5,
                "red_flags": [],
                "needs_followup": False,
                "key_points": []
            }
    
    async def _generate_followup_questions(self, original_question: InterviewQuestion, response: str, analysis: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions based on the response"""
        
        prompt = f"""
        Generate 1-2 follow-up questions based on this interview exchange:
        
        Original Question: {original_question.question}
        Response: {response}
        Analysis: {json.dumps(analysis, indent=2)}
        
        The follow-up questions should:
        1. Probe for specific examples if the response was vague
        2. Ask for clarification on unclear points
        3. Dig deeper into concerning areas
        4. Be natural and conversational
        
        Return as JSON array: ["question1", "question2"]
        """
        
        ai_response = await self.model.generate_content_async(prompt)
        
        try:
            questions = json.loads(ai_response.text)
            return questions if isinstance(questions, list) else []
        except json.JSONDecodeError:
            return []
    
    async def _calculate_overall_sentiment(self, responses: List[InterviewResponse]) -> float:
        """Calculate overall sentiment across all responses"""
        
        if not responses:
            return 0.0
        
        total_sentiment = sum(response.sentiment_score for response in responses)
        return total_sentiment / len(responses)
    
    async def _extract_key_insights(self, responses: List[InterviewResponse]) -> List[str]:
        """Extract key insights from the interview"""
        
        all_responses = "\n\n".join([
            f"Q: {r.question}\nA: {r.response}" for r in responses
        ])
        
        prompt = f"""
        Extract 5-7 key insights from this interview:
        
        {all_responses}
        
        Focus on:
        - Founder's strengths and weaknesses
        - Market opportunity assessment
        - Business model viability
        - Team capabilities
        - Risk factors
        
        Return as JSON array: ["insight1", "insight2", ...]
        """
        
        ai_response = await self.model.generate_content_async(prompt)
        
        try:
            insights = json.loads(ai_response.text)
            return insights if isinstance(insights, list) else []
        except json.JSONDecodeError:
            return ["Interview completed successfully"]
    
    async def _identify_red_flags(self, responses: List[InterviewResponse]) -> List[str]:
        """Identify red flags from the interview"""
        
        all_red_flags = []
        for response in responses:
            all_red_flags.extend(response.red_flags)
        
        # Remove duplicates and return unique red flags
        return list(set(all_red_flags))
    
    async def _save_session(self, session: InterviewSession):
        """Save interview session to database"""
        
        session_data = {
            'session_id': session.session_id,
            'startup_id': session.startup_id,
            'founder_name': session.founder_name,
            'founder_email': session.founder_email,
            'status': session.status.value,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'responses': [
                {
                    'question': r.question,
                    'response': r.response,
                    'timestamp': r.timestamp,
                    'sentiment_score': r.sentiment_score,
                    'confidence_score': r.confidence_score,
                    'red_flags': r.red_flags
                } for r in session.responses
            ],
            'overall_sentiment': session.overall_sentiment,
            'key_insights': session.key_insights,
            'red_flags': session.red_flags,
            'updated_at': datetime.utcnow()
        }
        
        self.db.collection('interview_sessions').document(session.session_id).set(session_data, merge=True)
        logger.info(f"Session saved: {session.session_id}")
    
    async def _generate_interview_report(self, session: InterviewSession):
        """Generate comprehensive interview report"""
        
        prompt = f"""
        Generate a comprehensive interview report based on this session:
        
        Founder: {session.founder_name}
        Overall Sentiment: {session.overall_sentiment}
        Key Insights: {json.dumps(session.key_insights, indent=2)}
        Red Flags: {json.dumps(session.red_flags, indent=2)}
        
        Include:
        1. Executive Summary
        2. Founder Assessment
        3. Business Opportunity Analysis
        4. Risk Assessment
        5. Investment Recommendation
        
        Format as a professional investment memo section.
        """
        
        ai_response = await self.model.generate_content_async(prompt)
        
        # Save report to database
        report_data = {
            'session_id': session.session_id,
            'startup_id': session.startup_id,
            'report_content': ai_response.text,
            'generated_at': datetime.utcnow()
        }
        
        self.db.collection('interview_reports').add(report_data)
        logger.info(f"Interview report generated for session: {session.session_id}")

# Usage example
async def main():
    """Example usage of the interview agent"""
    
    agent = StartupInterviewAgent(project_id="your-project-id")
    
    session = await agent.conduct_interview(
        startup_id="startup-123",
        founder_email="founder@startup.com",
        founder_name="John Doe"
    )
    
    print(f"Interview completed. Overall sentiment: {session.overall_sentiment:.2f}")
    print(f"Key insights: {session.key_insights}")

if __name__ == "__main__":
    asyncio.run(main())
