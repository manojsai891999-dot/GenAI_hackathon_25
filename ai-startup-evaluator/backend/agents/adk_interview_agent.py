import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

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

from models.database import get_db, create_tables
from models.schemas import InterviewResponse, InterviewSession
from services.gcs_service import gcs_service

logger = logging.getLogger(__name__)

# Predefined investment-related questions
INVESTMENT_QUESTIONS = [
    {
        "question": "What problem is your startup solving?",
        "category": "problem",
        "follow_up_questions": [
            "How did you identify this problem?",
            "What makes this problem urgent and important?",
            "How big is this problem in terms of market size?"
        ]
    },
    {
        "question": "Who are your target customers?",
        "category": "customers",
        "follow_up_questions": [
            "How do you reach your target customers?",
            "What's your customer acquisition strategy?",
            "How do you validate product-market fit?"
        ]
    },
    {
        "question": "What is your current traction (users, revenue, growth)?",
        "category": "traction",
        "follow_up_questions": [
            "What are your key growth metrics?",
            "How has your growth rate changed over time?",
            "What's driving your growth?"
        ]
    },
    {
        "question": "What is your business model?",
        "category": "business_model",
        "follow_up_questions": [
            "How do you price your product/service?",
            "What's your customer lifetime value?",
            "How scalable is your business model?"
        ]
    },
    {
        "question": "Who are your competitors and how are you different?",
        "category": "competition",
        "follow_up_questions": [
            "What's your competitive advantage?",
            "How do you plan to maintain your differentiation?",
            "What barriers to entry exist in your market?"
        ]
    },
    {
        "question": "What is your fundraising goal and how will you use the capital?",
        "category": "fundraising",
        "follow_up_questions": [
            "What milestones will this funding help you achieve?",
            "How long will this funding last?",
            "What's your next funding round timeline?"
        ]
    }
]

class InterviewAgent:
    def __init__(self):
        self.agent = Agent(
            name="interview_agent",
            model="gemini-2.0-flash",
            description="AI Interview Agent for Startup Founder Evaluation",
            instruction="""
            You are an expert AI interviewer conducting investment-focused interviews with startup founders.
            
            Your role is to:
            1. Ask predefined investment-related questions in a conversational manner
            2. Listen actively to responses and ask relevant follow-up questions
            3. Analyze responses for insights, risks, and opportunities
            4. Maintain a professional yet friendly tone
            5. Guide the conversation naturally while covering all key topics
            
            Guidelines:
            - Be conversational and engaging, not robotic
            - Ask follow-up questions based on the founder's responses
            - Probe deeper when answers are vague or incomplete
            - Show genuine interest in their business
            - Maintain professional boundaries while being personable
            - Take notes on key insights, risks, and positive signals
            """
        )
        
        # Initialize memory for structured storage
        self.memory = Memory()
        
        # Create database tables only if not in production
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
    
    def start_interview_session(self, founder_name: str, startup_name: Optional[str] = None) -> Dict[str, Any]:
        """Start a new interview session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create ADK session for conversation flow
            adk_session = ADKSession(
                session_id=session_id,
                user_id=founder_name,
                context={
                    "founder_name": founder_name,
                    "startup_name": startup_name,
                    "interview_type": "investment_evaluation",
                    "questions_asked": [],
                    "current_question_index": 0,
                    "session_start_time": datetime.now().isoformat()
                }
            )
            
            # Store session in database
            with next(get_db()) as db:
                interview_session = InterviewSession(
                    session_id=session_id,
                    founder_name=founder_name,
                    startup_name=startup_name,
                    session_status="active",
                    total_questions=len(INVESTMENT_QUESTIONS),
                    session_start_time=datetime.now()
                )
                db.add(interview_session)
                db.commit()
            
            # Generate greeting message
            greeting = self._generate_greeting(founder_name, startup_name)
            
            # Store initial context in memory
            self.memory.store({
                "session_id": session_id,
                "founder_name": founder_name,
                "startup_name": startup_name,
                "session_start_time": datetime.now().isoformat(),
                "questions_answered": 0,
                "insights_gathered": {},
                "red_flags": [],
                "positive_signals": [],
                "conversation_history": []
            })
            
            return {
                "status": "success",
                "session_id": session_id,
                "greeting": greeting,
                "total_questions": len(INVESTMENT_QUESTIONS),
                "session_data": {
                    "session_id": session_id,
                    "founder_name": founder_name,
                    "startup_name": startup_name,
                    "adk_session": adk_session
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to start interview session: {str(e)}")
            return {"status": "error", "error_message": str(e)}
    
    def process_founder_response(self, session_data: Dict[str, Any], response: str) -> Dict[str, Any]:
        """Process founder's response and generate next question"""
        try:
            session_id = session_data["session_id"]
            founder_name = session_data["founder_name"]
            
            # Retrieve session memory
            memory_data = self.memory.retrieve({"session_id": session_id})
            if not memory_data:
                return {"status": "error", "error_message": "Session not found"}
            
            # Get current question index
            current_index = memory_data.get("questions_answered", 0)
            
            if current_index >= len(INVESTMENT_QUESTIONS):
                return self._complete_interview(session_data, memory_data)
            
            # Get current question
            current_question = INVESTMENT_QUESTIONS[current_index]
            
            # Analyze the response
            analysis = self._analyze_response(response, current_question["category"])
            
            # Store response in database
            self._store_response(
                session_id=session_id,
                founder_name=founder_name,
                question=current_question["question"],
                response=response,
                category=current_question["category"],
                analysis=analysis
            )
            
            # Update memory with insights
            self._update_memory_with_insights(session_id, analysis)
            
            # Determine next action
            next_action = self._determine_next_action(current_index, analysis, response)
            
            # Generate next message
            next_message = self._generate_next_message(
                current_question, 
                response, 
                analysis, 
                next_action,
                current_index,
                len(INVESTMENT_QUESTIONS)
            )
            
            # Update session progress
            self._update_session_progress(session_id, current_index + 1)
            
            return {
                "status": "success",
                "next_message": next_message,
                "current_question": current_question["question"],
                "current_category": current_question["category"],
                "analysis": analysis,
                "progress": {
                    "questions_answered": current_index + 1,
                    "total_questions": len(INVESTMENT_QUESTIONS),
                    "progress_percentage": round(((current_index + 1) / len(INVESTMENT_QUESTIONS)) * 100, 1)
                },
                "next_action": next_action
            }
            
        except Exception as e:
            logger.error(f"Failed to process founder response: {str(e)}")
            return {"status": "error", "error_message": str(e)}
    
    def _generate_greeting(self, founder_name: str, startup_name: Optional[str]) -> str:
        """Generate personalized greeting message"""
        if startup_name:
            return f"""Hello {founder_name}! Thank you for taking the time to speak with me today about {startup_name}. 

I'm here to conduct an investment evaluation interview to better understand your business, market opportunity, and growth potential. This will be a conversational discussion where I'll ask you about various aspects of your startup.

The interview will cover topics like the problem you're solving, your target customers, current traction, business model, competitive landscape, and your fundraising plans. Feel free to provide as much detail as you'd like, and I may ask follow-up questions to dive deeper into specific areas.

Are you ready to begin? Let's start with the first question."""
        else:
            return f"""Hello {founder_name}! Thank you for taking the time to speak with me today about your startup. 

I'm here to conduct an investment evaluation interview to better understand your business, market opportunity, and growth potential. This will be a conversational discussion where I'll ask you about various aspects of your startup.

The interview will cover topics like the problem you're solving, your target customers, current traction, business model, competitive landscape, and your fundraising plans. Feel free to provide as much detail as you'd like, and I may ask follow-up questions to dive deeper into specific areas.

Are you ready to begin? Let's start with the first question."""
    
    def _analyze_response(self, response: str, category: str) -> Dict[str, Any]:
        """Analyze founder's response for insights, risks, and signals"""
        try:
            # Use the agent to analyze the response
            analysis_prompt = f"""
            Analyze this founder's response about {category}:
            
            Response: "{response}"
            
            Please provide:
            1. Key insights (2-3 main points)
            2. Red flags (any concerning aspects)
            3. Positive signals (strong points)
            4. Sentiment score (-1 to 1)
            5. Confidence score (0 to 1) - how confident/clear was the response
            6. Follow-up suggestions (what to ask next)
            
            Format as JSON.
            """
            
            # For now, we'll use a simple analysis approach
            # In production, this would use the ADK agent's analysis capabilities
            analysis = {
                "key_insights": self._extract_insights(response, category),
                "red_flags": self._identify_red_flags(response, category),
                "positive_signals": self._identify_positive_signals(response, category),
                "sentiment_score": self._calculate_sentiment(response),
                "confidence_score": self._calculate_confidence(response),
                "follow_up_suggestions": self._suggest_follow_ups(response, category)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze response: {str(e)}")
            return {
                "key_insights": [],
                "red_flags": [],
                "positive_signals": [],
                "sentiment_score": 0.0,
                "confidence_score": 0.5,
                "follow_up_suggestions": []
            }
    
    def _extract_insights(self, response: str, category: str) -> List[str]:
        """Extract key insights from the response"""
        insights = []
        response_lower = response.lower()
        
        if category == "problem":
            if "market" in response_lower and ("billion" in response_lower or "million" in response_lower):
                insights.append("Market size mentioned")
            if "urgent" in response_lower or "critical" in response_lower:
                insights.append("Problem urgency highlighted")
        
        elif category == "customers":
            if "enterprise" in response_lower:
                insights.append("Enterprise customer focus")
            if "b2b" in response_lower or "b2c" in response_lower:
                insights.append("Clear customer segment identified")
        
        elif category == "traction":
            if any(metric in response_lower for metric in ["revenue", "users", "growth", "customers"]):
                insights.append("Quantifiable metrics provided")
            if "%" in response or "x" in response_lower:
                insights.append("Growth metrics mentioned")
        
        elif category == "business_model":
            if any(word in response_lower for word in ["subscription", "saas", "recurring"]):
                insights.append("Recurring revenue model")
            if "pricing" in response_lower or "$" in response:
                insights.append("Pricing strategy discussed")
        
        elif category == "competition":
            if "different" in response_lower or "unique" in response_lower:
                insights.append("Differentiation strategy mentioned")
            if "advantage" in response_lower or "moat" in response_lower:
                insights.append("Competitive advantage identified")
        
        elif category == "fundraising":
            if "$" in response or "million" in response_lower or "billion" in response_lower:
                insights.append("Specific funding amount mentioned")
            if "milestone" in response_lower or "goal" in response_lower:
                insights.append("Clear funding goals outlined")
        
        return insights
    
    def _identify_red_flags(self, response: str, category: str) -> List[str]:
        """Identify potential red flags in the response"""
        red_flags = []
        response_lower = response.lower()
        
        # Generic red flags
        if len(response.strip()) < 20:
            red_flags.append("Very brief response - may lack depth")
        
        if "don't know" in response_lower or "not sure" in response_lower:
            red_flags.append("Uncertainty about key aspects")
        
        if "confidential" in response_lower or "can't share" in response_lower:
            red_flags.append("Lack of transparency")
        
        # Category-specific red flags
        if category == "traction" and "no" in response_lower and any(metric in response_lower for metric in ["revenue", "users", "customers"]):
            red_flags.append("No traction metrics provided")
        
        if category == "competition" and "no competition" in response_lower:
            red_flags.append("Claims no competition - may indicate market misunderstanding")
        
        return red_flags
    
    def _identify_positive_signals(self, response: str, category: str) -> List[str]:
        """Identify positive signals in the response"""
        positive_signals = []
        response_lower = response.lower()
        
        # Generic positive signals
        if len(response.strip()) > 100:
            positive_signals.append("Detailed, comprehensive response")
        
        if any(word in response_lower for word in ["data", "metrics", "numbers", "statistics"]):
            positive_signals.append("Data-driven approach")
        
        if any(word in response_lower for word in ["proven", "validated", "tested", "evidence"]):
            positive_signals.append("Evidence-based claims")
        
        # Category-specific positive signals
        if category == "problem" and "validated" in response_lower:
            positive_signals.append("Problem validation demonstrated")
        
        if category == "traction" and any(metric in response_lower for metric in ["growth", "increase", "improve"]):
            positive_signals.append("Growth trajectory shown")
        
        return positive_signals
    
    def _calculate_sentiment(self, response: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        positive_words = ["excited", "confident", "strong", "growing", "successful", "optimistic", "positive"]
        negative_words = ["challenging", "difficult", "struggling", "concerned", "worried", "negative"]
        
        response_lower = response.lower()
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_confidence(self, response: str) -> float:
        """Calculate confidence score (0 to 1)"""
        confidence_indicators = ["confident", "sure", "certain", "proven", "validated", "data shows"]
        uncertainty_indicators = ["maybe", "perhaps", "might", "could be", "not sure", "don't know"]
        
        response_lower = response.lower()
        confidence_count = sum(1 for word in confidence_indicators if word in response_lower)
        uncertainty_count = sum(1 for word in uncertainty_indicators if word in response_lower)
        
        # Base confidence on response length and specificity
        length_score = min(len(response.strip()) / 200, 1.0)  # Max at 200 chars
        specificity_score = 1.0 if any(char.isdigit() for char in response) else 0.5
        
        base_confidence = (length_score + specificity_score) / 2
        
        # Adjust based on confidence/uncertainty indicators
        if confidence_count > uncertainty_count:
            return min(base_confidence + 0.2, 1.0)
        elif uncertainty_count > confidence_count:
            return max(base_confidence - 0.2, 0.0)
        else:
            return base_confidence
    
    def _suggest_follow_ups(self, response: str, category: str) -> List[str]:
        """Suggest follow-up questions based on the response"""
        follow_ups = []
        response_lower = response.lower()
        
        if category == "problem" and "market" in response_lower:
            follow_ups.append("How did you validate the market size?")
        
        if category == "traction" and "growth" in response_lower:
            follow_ups.append("What's driving this growth?")
        
        if category == "competition" and "different" in response_lower:
            follow_ups.append("How do you maintain this differentiation?")
        
        return follow_ups
    
    def _store_response(self, session_id: str, founder_name: str, question: str, 
                       response: str, category: str, analysis: Dict[str, Any]) -> None:
        """Store response in CloudSQL database"""
        try:
            with next(get_db()) as db:
                interview_response = InterviewResponse(
                    session_id=session_id,
                    founder_name=founder_name,
                    question=question,
                    response=response,
                    question_category=category,
                    sentiment_score=analysis.get("sentiment_score", 0.0),
                    confidence_score=analysis.get("confidence_score", 0.5),
                    key_insights=analysis.get("key_insights", []),
                    red_flags=analysis.get("red_flags", []),
                    positive_signals=analysis.get("positive_signals", [])
                )
                db.add(interview_response)
                db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store response: {str(e)}")
    
    def _update_memory_with_insights(self, session_id: str, analysis: Dict[str, Any]) -> None:
        """Update memory with new insights"""
        try:
            memory_data = self.memory.retrieve({"session_id": session_id})
            if memory_data:
                # Update insights
                insights = memory_data.get("insights_gathered", {})
                for insight in analysis.get("key_insights", []):
                    insights[insight] = insights.get(insight, 0) + 1
                
                # Update red flags and positive signals
                red_flags = memory_data.get("red_flags", [])
                red_flags.extend(analysis.get("red_flags", []))
                
                positive_signals = memory_data.get("positive_signals", [])
                positive_signals.extend(analysis.get("positive_signals", []))
                
                # Store updated memory
                self.memory.store({
                    "session_id": session_id,
                    "insights_gathered": insights,
                    "red_flags": red_flags,
                    "positive_signals": positive_signals
                })
                
        except Exception as e:
            logger.error(f"Failed to update memory: {str(e)}")
    
    def _determine_next_action(self, current_index: int, analysis: Dict[str, Any], response: str) -> str:
        """Determine next action based on response analysis"""
        # If response is very brief or lacks detail, ask follow-up
        if len(response.strip()) < 50:
            return "follow_up"
        
        # If there are red flags, probe deeper
        if analysis.get("red_flags"):
            return "follow_up"
        
        # If response is comprehensive, move to next question
        if analysis.get("confidence_score", 0) > 0.7:
            return "next_question"
        
        # Default to follow-up for medium confidence responses
        return "follow_up"
    
    def _generate_next_message(self, current_question: Dict[str, Any], response: str, 
                             analysis: Dict[str, Any], next_action: str, 
                             current_index: int, total_questions: int) -> str:
        """Generate the next message based on analysis and action"""
        if next_action == "follow_up" and current_question.get("follow_up_questions"):
            # Ask a follow-up question
            follow_up = current_question["follow_up_questions"][0]  # Use first follow-up
            return f"Thank you for that response. {follow_up}"
        
        elif next_action == "next_question" and current_index + 1 < total_questions:
            # Move to next main question
            next_question = INVESTMENT_QUESTIONS[current_index + 1]
            return f"Great, thank you for that detailed response. Let's move on to the next topic. {next_question['question']}"
        
        elif current_index + 1 >= total_questions:
            # Interview is complete
            return "Thank you for answering all the questions. Let me prepare a summary of our discussion."
        
        else:
            # Default acknowledgment
            return "Thank you for that response. Could you elaborate a bit more on that point?"
    
    def _update_session_progress(self, session_id: str, questions_answered: int) -> None:
        """Update session progress in database"""
        try:
            with next(get_db()) as db:
                session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
                if session:
                    session.questions_answered = questions_answered
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Failed to update session progress: {str(e)}")
    
    def _complete_interview(self, session_data: Dict[str, Any], memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the interview and generate summary report"""
        try:
            session_id = session_data["session_id"]
            founder_name = session_data["founder_name"]
            startup_name = session_data.get("startup_name", "Unknown Startup")
            
            # Generate summary report
            summary_report = self._generate_summary_report(session_data, memory_data)
            
            # Save report to GCS
            gcs_path = self._save_report_to_gcs(session_id, founder_name, summary_report)
            
            # Update session status
            self._update_session_completion(session_id, summary_report, gcs_path)
            
            return {
                "status": "success",
                "interview_completed": True,
                "summary_report": summary_report,
                "gcs_path": gcs_path,
                "completion_message": f"Thank you, {founder_name}! The interview is now complete. I've prepared a comprehensive summary report that will be available for review."
            }
            
        except Exception as e:
            logger.error(f"Failed to complete interview: {str(e)}")
            return {"status": "error", "error_message": str(e)}
    
    def _generate_summary_report(self, session_data: Dict[str, Any], memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        session_id = session_data["session_id"]
        founder_name = session_data["founder_name"]
        startup_name = session_data.get("startup_name", "Unknown Startup")
        
        # Retrieve all responses for this session
        with next(get_db()) as db:
            responses = db.query(InterviewResponse).filter(
                InterviewResponse.session_id == session_id
            ).order_by(InterviewResponse.response_timestamp).all()
        
        # Calculate overall metrics
        total_responses = len(responses)
        avg_sentiment = sum(r.sentiment_score for r in responses) / total_responses if responses else 0
        avg_confidence = sum(r.confidence_score for r in responses) / total_responses if responses else 0
        
        # Aggregate insights
        all_insights = []
        all_red_flags = []
        all_positive_signals = []
        
        for response in responses:
            all_insights.extend(response.key_insights or [])
            all_red_flags.extend(response.red_flags or [])
            all_positive_signals.extend(response.positive_signals or [])
        
        # Generate report
        report = {
            "interview_summary": {
                "founder_name": founder_name,
                "startup_name": startup_name,
                "session_id": session_id,
                "interview_date": datetime.now().isoformat(),
                "total_questions": total_responses,
                "duration_minutes": 30  # Estimated
            },
            "key_insights": {
                "strengths": list(set(all_positive_signals)),
                "risks": list(set(all_red_flags)),
                "opportunities": self._identify_opportunities(responses),
                "competitive_landscape": self._analyze_competition(responses)
            },
            "fundraising_details": self._extract_fundraising_info(responses),
            "overall_assessment": {
                "sentiment_score": avg_sentiment,
                "confidence_score": avg_confidence,
                "recommendation": self._generate_recommendation(avg_sentiment, avg_confidence, all_red_flags),
                "next_steps": self._suggest_next_steps(all_red_flags, all_positive_signals)
            },
            "detailed_responses": [
                {
                    "question": r.question,
                    "response": r.response,
                    "category": r.question_category,
                    "insights": r.key_insights,
                    "sentiment": r.sentiment_score,
                    "confidence": r.confidence_score
                }
                for r in responses
            ]
        }
        
        return report
    
    def _identify_opportunities(self, responses: List[InterviewResponse]) -> List[str]:
        """Identify growth opportunities from responses"""
        opportunities = []
        
        for response in responses:
            if response.question_category == "traction" and response.positive_signals:
                opportunities.append("Strong growth trajectory")
            if response.question_category == "market" and "large" in response.response.lower():
                opportunities.append("Large addressable market")
            if response.question_category == "competition" and "unique" in response.response.lower():
                opportunities.append("Unique competitive positioning")
        
        return list(set(opportunities))
    
    def _analyze_competition(self, responses: List[InterviewResponse]) -> Dict[str, Any]:
        """Analyze competitive landscape from responses"""
        competition_responses = [r for r in responses if r.question_category == "competition"]
        
        if not competition_responses:
            return {"analysis": "No competition data provided"}
        
        response = competition_responses[0]
        return {
            "analysis": response.response,
            "differentiation_mentioned": "different" in response.response.lower(),
            "competitive_advantage_clear": response.confidence_score > 0.7
        }
    
    def _extract_fundraising_info(self, responses: List[InterviewResponse]) -> Dict[str, Any]:
        """Extract fundraising information from responses"""
        fundraising_responses = [r for r in responses if r.question_category == "fundraising"]
        
        if not fundraising_responses:
            return {"funding_goal": "Not specified", "use_of_funds": "Not specified"}
        
        response = fundraising_responses[0]
        return {
            "funding_goal": self._extract_funding_amount(response.response),
            "use_of_funds": response.response,
            "funding_timeline": "Not specified",
            "funding_readiness": "High" if response.confidence_score > 0.7 else "Medium"
        }
    
    def _extract_funding_amount(self, response: str) -> str:
        """Extract funding amount from response"""
        import re
        amounts = re.findall(r'\$[\d,]+(?:\.\d+)?[KMB]?', response)
        return amounts[0] if amounts else "Not specified"
    
    def _generate_recommendation(self, sentiment: float, confidence: float, red_flags: List[str]) -> str:
        """Generate investment recommendation"""
        if len(red_flags) > 3:
            return "Proceed with caution - multiple red flags identified"
        elif sentiment > 0.5 and confidence > 0.7:
            return "Strong candidate - proceed to next stage"
        elif sentiment > 0.2 and confidence > 0.5:
            return "Promising candidate - requires further evaluation"
        else:
            return "Not recommended - low confidence or negative sentiment"
    
    def _suggest_next_steps(self, red_flags: List[str], positive_signals: List[str]) -> List[str]:
        """Suggest next steps based on analysis"""
        next_steps = []
        
        if red_flags:
            next_steps.append("Address identified red flags in follow-up discussion")
        
        if len(positive_signals) > 3:
            next_steps.append("Schedule detailed due diligence meeting")
        
        next_steps.append("Review financial projections and business plan")
        next_steps.append("Conduct reference checks with customers and partners")
        
        return next_steps
    
    def _save_report_to_gcs(self, session_id: str, founder_name: str, report: Dict[str, Any]) -> str:
        """Save summary report to Google Cloud Storage"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/{founder_name}_{session_id}_{timestamp}"
            
            # Save as JSON
            json_path = f"{filename}.json"
            gcs_service.upload_json(report, json_path)
            
            # Save as text summary
            text_summary = self._generate_text_summary(report)
            text_path = f"{filename}.txt"
            gcs_service.upload_text(text_summary, text_path)
            
            return json_path
            
        except Exception as e:
            logger.error(f"Failed to save report to GCS: {str(e)}")
            return ""
    
    def _generate_text_summary(self, report: Dict[str, Any]) -> str:
        """Generate human-readable text summary"""
        summary = f"""
INVESTMENT INTERVIEW SUMMARY REPORT
====================================

Founder: {report['interview_summary']['founder_name']}
Startup: {report['interview_summary']['startup_name']}
Date: {report['interview_summary']['interview_date']}
Session ID: {report['interview_summary']['session_id']}

KEY INSIGHTS
============
Strengths:
{chr(10).join(f"- {strength}" for strength in report['key_insights']['strengths'])}

Risks:
{chr(10).join(f"- {risk}" for risk in report['key_insights']['risks'])}

Opportunities:
{chr(10).join(f"- {opp}" for opp in report['key_insights']['opportunities'])}

FUNDRAISING DETAILS
===================
Funding Goal: {report['fundraising_details']['funding_goal']}
Use of Funds: {report['fundraising_details']['use_of_funds']}
Funding Readiness: {report['fundraising_details']['funding_readiness']}

OVERALL ASSESSMENT
==================
Sentiment Score: {report['overall_assessment']['sentiment_score']:.2f}
Confidence Score: {report['overall_assessment']['confidence_score']:.2f}
Recommendation: {report['overall_assessment']['recommendation']}

Next Steps:
{chr(10).join(f"- {step}" for step in report['overall_assessment']['next_steps'])}

COMPETITIVE LANDSCAPE
=====================
{report['key_insights']['competitive_landscape']['analysis']}
"""
        return summary
    
    def _update_session_completion(self, session_id: str, summary_report: Dict[str, Any], gcs_path: str) -> None:
        """Update session status to completed"""
        try:
            with next(get_db()) as db:
                session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
                if session:
                    session.session_status = "completed"
                    session.session_end_time = datetime.now()
                    session.duration_minutes = 30  # Estimated
                    session.overall_sentiment = summary_report['overall_assessment']['sentiment_score']
                    session.overall_confidence = summary_report['overall_assessment']['confidence_score']
                    session.key_insights = summary_report['key_insights']['strengths']
                    session.red_flags = summary_report['key_insights']['risks']
                    session.positive_signals = summary_report['key_insights']['strengths']
                    session.summary_report_gcs_path = gcs_path
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Failed to update session completion: {str(e)}")

# Create global instance
interview_agent = InterviewAgent()