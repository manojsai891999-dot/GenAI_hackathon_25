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
    VoiceInterviewAgentInput,
    VoiceInterviewAgentOutput,
    InterviewCreate
)
from ..services.gcs_service import gcs_service, get_interview_transcript_path, get_interview_audio_path

logger = logging.getLogger(__name__)

def convert_audio_to_wav(audio_file_path: str) -> dict:
    """Convert audio file to WAV format for speech recognition"""
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        # Convert to WAV format
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            audio.export(temp_wav.name, format="wav")
            return {"status": "success", "wav_path": temp_wav.name}
    except Exception as e:
        logger.error(f"Audio conversion failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def transcribe_audio_to_text(wav_file_path: str) -> dict:
    """Convert speech to text using speech recognition"""
    try:
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            # Record the audio
            audio_data = recognizer.record(source)
        
        # Use Google Speech Recognition
        try:
            transcript = recognizer.recognize_google(audio_data)
            return {"status": "success", "transcript": transcript}
        except sr.UnknownValueError:
            return {"status": "error", "error_message": "Could not understand audio"}
        except sr.RequestError as e:
            return {"status": "error", "error_message": f"Speech recognition service error: {str(e)}"}
    
    except Exception as e:
        logger.error(f"Speech transcription failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def start_live_voice_interview(startup_id: int, founder_name: str, interview_type: str = "comprehensive") -> dict:
    """Start a live voice interview session with natural conversation flow"""
    try:
        session_id = f"voice_interview_{startup_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize conversation state
        conversation_state = {
            "session_id": session_id,
            "startup_id": startup_id,
            "founder_name": founder_name,
            "interview_type": interview_type,
            "start_time": datetime.now().isoformat(),
            "current_topic": "introduction",
            "conversation_history": [],
            "questions_asked": [],
            "follow_up_needed": [],
            "insights_gathered": {},
            "rapport_level": 0.5,  # Start neutral
            "energy_level": "medium"
        }
        
        # Generate opening message
        opening_message = generate_conversational_opening(founder_name, interview_type)
        
        return {
            "status": "success",
            "session_data": conversation_state,
            "opening_message": opening_message,
            "next_action": "wait_for_response"
        }
    except Exception as e:
        logger.error(f"Failed to start live voice interview: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_conversational_opening(founder_name: str, interview_type: str) -> str:
    """Generate a warm, conversational opening for the interview"""
    openings = {
        "comprehensive": f"Hi {founder_name}! Thanks for taking the time to chat with me today. I'm really excited to learn more about what you're building. Before we dive in, how are you doing? And maybe you could start by telling me a bit about yourself and what inspired you to start this company?",
        
        "screening": f"Hello {founder_name}! Great to meet you. I've been looking forward to our conversation. I know your time is valuable, so I'd love to hear your story. Could you give me the elevator pitch - what's your company all about and what problem are you solving?",
        
        "deep_dive": f"Hi {founder_name}! Thanks for joining me for this deeper conversation about your company. I've reviewed some initial materials, and I'm impressed by what I've seen so far. I'd love to dig into the details with you. Shall we start with you telling me how the business has evolved since you first started?"
    }
    
    return openings.get(interview_type, openings["comprehensive"])

def process_founder_response(session_data: dict, founder_response: str, audio_metadata: dict = None) -> dict:
    """Process founder's response and generate next conversational question"""
    try:
        # Analyze the response
        response_analysis = analyze_response_content(founder_response, session_data["current_topic"])
        
        # Update conversation history
        session_data["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "founder",
            "content": founder_response,
            "topic": session_data["current_topic"],
            "analysis": response_analysis,
            "audio_metadata": audio_metadata
        })
        
        # Update insights and rapport
        session_data["insights_gathered"].update(response_analysis.get("insights", {}))
        session_data["rapport_level"] = calculate_rapport_level(session_data["conversation_history"])
        
        # Generate next question or follow-up
        next_interaction = generate_next_conversational_question(session_data, response_analysis)
        
        # Add interviewer response to history
        session_data["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "interviewer",
            "content": next_interaction["message"],
            "topic": next_interaction["topic"],
            "question_type": next_interaction["type"]
        })
        
        session_data["current_topic"] = next_interaction["topic"]
        
        return {
            "status": "success",
            "next_message": next_interaction["message"],
            "current_topic": next_interaction["topic"],
            "conversation_progress": calculate_interview_progress(session_data),
            "session_data": session_data
        }
    except Exception as e:
        logger.error(f"Failed to process founder response: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def analyze_response_content(response: str, current_topic: str) -> dict:
    """Analyze founder's response for content, sentiment, and insights"""
    try:
        response_lower = response.lower()
        word_count = len(response.split())
        
        # Sentiment analysis
        positive_words = ["excited", "confident", "growing", "successful", "strong", "excellent", "passionate", "love", "amazing", "fantastic"]
        negative_words = ["challenging", "difficult", "struggling", "worried", "concerned", "problem", "issue", "hard", "tough"]
        
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        sentiment_score = 0.5  # neutral
        if positive_count + negative_count > 0:
            sentiment_score = positive_count / (positive_count + negative_count)
        
        # Extract key insights based on topic
        insights = extract_topic_insights(response_lower, current_topic)
        
        # Assess response quality
        quality_score = assess_response_quality(response, current_topic, word_count)
        
        return {
            "word_count": word_count,
            "sentiment_score": sentiment_score,
            "quality_score": quality_score,
            "insights": insights,
            "key_phrases": extract_key_phrases(response_lower),
            "needs_follow_up": quality_score < 0.6 or word_count < 20
        }
    except Exception as e:
        logger.error(f"Response analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_next_conversational_question(session_data: dict, response_analysis: dict) -> dict:
    """Generate the next question in a natural, conversational way"""
    try:
        conversation_history = session_data["conversation_history"]
        current_topic = session_data["current_topic"]
        rapport_level = session_data["rapport_level"]
        
        # Determine if we need follow-up or can move to next topic
        if response_analysis.get("needs_follow_up", False):
            return generate_follow_up_question(session_data, response_analysis)
        
        # Check if current topic is sufficiently covered
        topic_coverage = calculate_topic_coverage(session_data, current_topic)
        if topic_coverage < 0.7:
            return generate_topic_continuation(session_data, current_topic)
        
        # Move to next topic
        next_topic = determine_next_topic(session_data)
        return generate_topic_transition(session_data, current_topic, next_topic)
        
    except Exception as e:
        logger.error(f"Failed to generate next question: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_follow_up_question(session_data: dict, response_analysis: dict) -> dict:
    """Generate a natural follow-up question to get more details"""
    founder_name = session_data["founder_name"]
    current_topic = session_data["current_topic"]
    
    follow_ups = {
        "introduction": [
            f"That's fascinating, {founder_name}! Can you tell me more about that specific moment when you realized this was a problem worth solving?",
            "I love the passion I'm hearing! What was the 'aha moment' that made you think this could be a big business?",
            "That sounds like quite a journey! What's been the most surprising thing you've learned so far?"
        ],
        "business_model": [
            "That's interesting! Can you walk me through a specific example of how that works in practice?",
            "I see! And how do your customers typically respond to that pricing model?",
            "Got it! What's been the biggest challenge in getting customers to adopt this approach?"
        ],
        "market_opportunity": [
            "That market size sounds significant! How did you validate those numbers?",
            "Interesting positioning! Can you give me a concrete example of how you're different from [competitor]?",
            "That's a compelling opportunity! What gives you confidence you can capture that market share?"
        ],
        "traction_metrics": [
            "Those are solid numbers! What's driving that growth specifically?",
            "That's impressive! Can you tell me about one of those customer success stories?",
            "Great progress! What's the story behind your best-performing customer segment?"
        ]
    }
    
    topic_questions = follow_ups.get(current_topic, follow_ups["introduction"])
    question = topic_questions[len(session_data["questions_asked"]) % len(topic_questions)]
    
    return {
        "message": question,
        "topic": current_topic,
        "type": "follow_up"
    }

def generate_topic_transition(session_data: dict, current_topic: str, next_topic: str) -> dict:
    """Generate smooth transitions between topics"""
    founder_name = session_data["founder_name"]
    
    transitions = {
        ("introduction", "business_model"): f"Thanks for sharing that background, {founder_name}! Now I'd love to understand the business side better. How exactly do you make money? Walk me through your revenue model.",
        
        ("business_model", "market_opportunity"): "That business model makes sense! Now let's talk about the market you're going after. How big is this opportunity, and who else is competing for it?",
        
        ("market_opportunity", "traction_metrics"): "The market opportunity sounds compelling! I'm curious about the traction you're seeing. What does your growth look like so far?",
        
        ("traction_metrics", "team_execution"): "Those metrics are encouraging! Let's talk about the team behind this growth. Tell me about your founding team and how you're thinking about scaling.",
        
        ("team_execution", "financial_planning"): "Sounds like you have a strong team! Now let's get into the numbers. What's your current financial situation and funding needs?",
        
        ("financial_planning", "product_development"): "Got it on the financials! I'd love to hear about your product roadmap. Where is the product heading next?",
        
        ("product_development", "risks_challenges"): "Exciting product plans! Now, every business faces challenges. What keeps you up at night as a founder?",
        
        ("risks_challenges", "vision_strategy"): f"I appreciate your honesty about those challenges, {founder_name}! Let's end on a high note - where do you see this company in 5 years?"
    }
    
    transition_key = (current_topic, next_topic)
    message = transitions.get(transition_key, f"Great! Now let's talk about {next_topic.replace('_', ' ')}.")
    
    return {
        "message": message,
        "topic": next_topic,
        "type": "transition"
    }

def get_interview_questions() -> dict:
    """Get predefined set of investor interview questions with conversational variants"""
    questions = {
        "business_model": {
            "primary": [
                "Walk me through how you make money. What's your revenue model?",
                "How do you price your product, and what's the thinking behind that strategy?",
                "Who exactly is your customer, and what problem are you solving for them?",
                "Tell me about your sales process. How do you actually get customers?"
            ],
            "follow_ups": [
                "Can you give me a specific example of that in action?",
                "How do customers typically respond to that approach?",
                "What's been the biggest surprise in your customer interactions?"
            ]
        },
        "market_opportunity": {
            "primary": [
                "How big is this market, and how fast is it growing?",
                "Who are you competing against, and how are you different?",
                "What barriers exist to entering this market?",
                "How do you plan to win market share?"
            ],
            "follow_ups": [
                "How did you validate those market size numbers?",
                "Can you give me a concrete example of your differentiation?",
                "What gives you confidence in your competitive position?"
            ]
        },
        "traction_metrics": {
            "primary": [
                "What do your revenue and growth numbers look like?",
                "How many customers do you have, and how sticky are they?",
                "What are your key metrics, and how are they trending?",
                "Can you share a customer success story that excites you?"
            ],
            "follow_ups": [
                "What's driving that specific growth?",
                "Tell me more about that customer's journey with you.",
                "What patterns do you see in your best customers?"
            ]
        },
        "team_execution": {
            "primary": [
                "Tell me about your founding team and what you each bring to the table.",
                "What are your biggest hiring needs in the next year?",
                "How do you think about scaling your team and culture?",
                "What's your leadership philosophy as you grow?"
            ],
            "follow_ups": [
                "What's a specific example of how that experience has helped?",
                "How do you plan to maintain culture as you scale?",
                "What's been your biggest learning as a leader?"
            ]
        },
        "financial_planning": {
            "primary": [
                "What's your current burn rate and runway situation?",
                "How much are you raising, and what will you use it for?",
                "What do your revenue projections look like?",
                "When do you expect to reach profitability?"
            ],
            "follow_ups": [
                "Walk me through the assumptions behind those projections.",
                "What's your biggest financial risk right now?",
                "How do you think about capital efficiency?"
            ]
        },
        "product_development": {
            "primary": [
                "What's on your product roadmap for the next year?",
                "How do you gather and prioritize customer feedback?",
                "What are your biggest technical challenges?",
                "How do you know you have product-market fit?"
            ],
            "follow_ups": [
                "Can you give me an example of how customer feedback changed your product?",
                "What's a specific technical challenge you're proud of solving?",
                "What evidence do you have of product-market fit?"
            ]
        },
        "risks_challenges": {
            "primary": [
                "What are the biggest risks to your business right now?",
                "What keeps you up at night as a founder?",
                "How would you handle a major competitor entering your space?",
                "What regulatory or market changes worry you most?"
            ],
            "follow_ups": [
                "How are you actively mitigating that risk?",
                "What would your response plan look like?",
                "How do you stay ahead of those potential challenges?"
            ]
        },
        "vision_strategy": {
            "primary": [
                "Where do you see this company in 5 years?",
                "What's your long-term vision and potential exit strategy?",
                "How do you think about geographic or market expansion?",
                "What strategic partnerships are you pursuing?"
            ],
            "follow_ups": [
                "What needs to happen for that vision to become reality?",
                "How do you balance long-term vision with short-term execution?",
                "What would success look like from an investor's perspective?"
            ]
        }
    }
    
    return {
        "status": "success",
        "questions": questions,
        "total_questions": sum(len(q_list["primary"]) for q_list in questions.values())
    }

def extract_topic_insights(response_lower: str, current_topic: str) -> dict:
    """Extract specific insights based on the current topic"""
    insights = {}
    
    topic_keywords = {
        "business_model": ["revenue", "pricing", "customers", "sales", "subscription", "b2b", "b2c"],
        "market_opportunity": ["market", "competitors", "competition", "differentiate", "market share", "tam", "sam"],
        "traction_metrics": ["revenue", "customers", "retention", "growth", "metrics", "kpi", "mrr", "arr"],
        "team_execution": ["team", "founder", "hiring", "culture", "experience", "cto", "ceo"],
        "financial_planning": ["burn rate", "funding", "runway", "profitability", "projections", "cash"],
        "product_development": ["product", "roadmap", "feedback", "technical", "development", "features"],
        "risks_challenges": ["risk", "challenge", "regulatory", "competitor", "problem", "threat"],
        "vision_strategy": ["vision", "strategy", "expansion", "partnership", "future", "exit"]
    }
    
    keywords = topic_keywords.get(current_topic, [])
    for keyword in keywords:
        if keyword in response_lower:
            insights[keyword] = True
    
    return insights

def extract_key_phrases(response_lower: str) -> list:
    """Extract key phrases from the response"""
    # Simple implementation - could be enhanced with NLP
    key_phrases = []
    
    # Look for specific business phrases
    business_phrases = [
        "product market fit", "go to market", "customer acquisition cost", "lifetime value",
        "monthly recurring revenue", "annual recurring revenue", "burn rate", "runway",
        "series a", "series b", "seed funding", "venture capital", "market size"
    ]
    
    for phrase in business_phrases:
        if phrase in response_lower:
            key_phrases.append(phrase)
    
    return key_phrases

def assess_response_quality(response: str, current_topic: str, word_count: int) -> float:
    """Assess the quality of a founder's response"""
    # Base score on word count (optimal range 50-200 words)
    if word_count < 20:
        length_score = 0.2
    elif word_count < 50:
        length_score = 0.6
    elif word_count <= 200:
        length_score = 1.0
    else:
        length_score = 0.8  # Too long might be rambling
    
    # Check for specificity (numbers, examples, concrete details)
    specificity_indicators = ["for example", "specifically", "$", "%", "customers", "months", "years"]
    specificity_count = sum(1 for indicator in specificity_indicators if indicator in response.lower())
    specificity_score = min(specificity_count / 3, 1.0)
    
    # Overall quality score
    quality_score = (length_score * 0.4 + specificity_score * 0.6)
    return round(quality_score, 2)

def calculate_rapport_level(conversation_history: list) -> float:
    """Calculate rapport level based on conversation dynamics"""
    if len(conversation_history) < 2:
        return 0.5
    
    founder_responses = [msg for msg in conversation_history if msg["speaker"] == "founder"]
    
    # Analyze response lengths (engaged founders give detailed responses)
    avg_response_length = sum(len(msg["content"].split()) for msg in founder_responses) / len(founder_responses)
    length_score = min(avg_response_length / 100, 1.0)  # Normalize to 100 words
    
    # Analyze sentiment trends
    sentiment_scores = [msg.get("analysis", {}).get("sentiment_score", 0.5) for msg in founder_responses]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
    
    # Calculate rapport (combination of engagement and sentiment)
    rapport = (length_score * 0.4 + avg_sentiment * 0.6)
    return round(rapport, 2)

def calculate_topic_coverage(session_data: dict, topic: str) -> float:
    """Calculate how well a topic has been covered"""
    topic_messages = [msg for msg in session_data["conversation_history"] 
                     if msg.get("topic") == topic and msg["speaker"] == "founder"]
    
    if not topic_messages:
        return 0.0
    
    # Check total words spoken on topic
    total_words = sum(len(msg["content"].split()) for msg in topic_messages)
    
    # Check insights gathered for this topic
    topic_insights = session_data["insights_gathered"]
    topic_keywords = {
        "business_model": ["revenue", "pricing", "customers", "sales"],
        "market_opportunity": ["market", "competitors", "competition", "differentiate"],
        "traction_metrics": ["revenue", "customers", "retention", "growth"],
        "team_execution": ["team", "founder", "hiring", "culture"],
        "financial_planning": ["burn rate", "funding", "runway", "profitability"],
        "product_development": ["product", "roadmap", "feedback", "technical"],
        "risks_challenges": ["risk", "challenge", "regulatory", "competitor"],
        "vision_strategy": ["vision", "strategy", "expansion", "partnership"]
    }
    
    expected_keywords = topic_keywords.get(topic, [])
    covered_keywords = sum(1 for keyword in expected_keywords if topic_insights.get(keyword, False))
    keyword_coverage = covered_keywords / len(expected_keywords) if expected_keywords else 0
    
    # Combine word count and keyword coverage
    word_score = min(total_words / 150, 1.0)  # Target ~150 words per topic
    coverage_score = (word_score * 0.4 + keyword_coverage * 0.6)
    
    return round(coverage_score, 2)

def determine_next_topic(session_data: dict) -> str:
    """Determine the next topic to discuss based on interview flow"""
    current_topic = session_data["current_topic"]
    
    # Standard interview flow
    topic_flow = [
        "introduction",
        "business_model", 
        "market_opportunity",
        "traction_metrics",
        "team_execution",
        "financial_planning",
        "product_development", 
        "risks_challenges",
        "vision_strategy"
    ]
    
    try:
        current_index = topic_flow.index(current_topic)
        if current_index < len(topic_flow) - 1:
            return topic_flow[current_index + 1]
        else:
            return "conclusion"  # End of interview
    except ValueError:
        return "business_model"  # Default fallback

def generate_topic_continuation(session_data: dict, current_topic: str) -> dict:
    """Generate a question to continue exploring the current topic"""
    questions_data = get_interview_questions()
    questions = questions_data["questions"]
    
    topic_questions = questions.get(current_topic, {}).get("primary", [])
    questions_asked_count = len([msg for msg in session_data["conversation_history"] 
                               if msg.get("topic") == current_topic and msg["speaker"] == "interviewer"])
    
    if questions_asked_count < len(topic_questions):
        question = topic_questions[questions_asked_count]
    else:
        # Use follow-up questions
        follow_ups = questions.get(current_topic, {}).get("follow_ups", ["Can you tell me more about that?"])
        question = follow_ups[questions_asked_count % len(follow_ups)]
    
    return {
        "message": question,
        "topic": current_topic,
        "type": "continuation"
    }

def calculate_interview_progress(session_data: dict) -> dict:
    """Calculate overall interview progress"""
    total_topics = 8  # Number of main topics
    current_topic = session_data["current_topic"]
    
    topic_flow = ["introduction", "business_model", "market_opportunity", "traction_metrics", 
                  "team_execution", "financial_planning", "product_development", "risks_challenges", "vision_strategy"]
    
    try:
        current_index = topic_flow.index(current_topic)
        progress_percentage = (current_index / len(topic_flow)) * 100
    except ValueError:
        progress_percentage = 0
    
    # Calculate time elapsed
    start_time = datetime.fromisoformat(session_data["start_time"])
    elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
    
    return {
        "current_topic": current_topic,
        "progress_percentage": round(progress_percentage, 1),
        "elapsed_minutes": round(elapsed_minutes, 1),
        "topics_completed": current_index,
        "total_topics": len(topic_flow),
        "estimated_remaining_minutes": max(0, round((len(topic_flow) - current_index) * 5, 1))  # ~5 min per topic
    }

def analyze_interview_responses(transcript: str, questions_context: dict = None) -> dict:
    """Analyze interview transcript against predefined questions for structured insights"""
    try:
        if not transcript or not transcript.strip():
            return {"status": "error", "error_message": "No transcript content to analyze"}
        
        transcript_lower = transcript.lower()
        
        # Get predefined questions
        questions_data = get_interview_questions()
        if questions_data["status"] != "success":
            return questions_data
        
        questions = questions_data["questions"]
        
        # Analyze coverage of different topic areas
        topic_coverage = {}
        for topic, topic_questions in questions.items():
            coverage_score = 0
            topic_keywords = {
                "business_model": ["revenue", "pricing", "customers", "sales", "business model"],
                "market_opportunity": ["market", "competitors", "competition", "differentiate", "market share"],
                "traction_metrics": ["revenue", "customers", "retention", "growth", "metrics", "kpi"],
                "team_execution": ["team", "founder", "hiring", "culture", "experience"],
                "financial_planning": ["burn rate", "funding", "runway", "profitability", "projections"],
                "product_development": ["product", "roadmap", "feedback", "technical", "development"],
                "risks_challenges": ["risk", "challenge", "regulatory", "competitor", "problem"],
                "vision_strategy": ["vision", "strategy", "expansion", "partnership", "future"]
            }
            
            keywords = topic_keywords.get(topic, [])
            keyword_mentions = sum(1 for keyword in keywords if keyword in transcript_lower)
            coverage_score = min(keyword_mentions / len(keywords), 1.0) if keywords else 0
            
            topic_coverage[topic] = {
                "coverage_score": round(coverage_score, 2),
                "keywords_found": [kw for kw in keywords if kw in transcript_lower],
                "assessment": "comprehensive" if coverage_score > 0.7 else "partial" if coverage_score > 0.3 else "minimal"
            }
        
        # Sentiment analysis with business context
        positive_indicators = [
            "excited", "confident", "strong", "excellent", "successful", "growing", "profitable",
            "traction", "momentum", "opportunity", "optimistic", "passionate", "committed"
        ]
        negative_indicators = [
            "concerned", "worried", "challenging", "difficult", "struggling", "uncertain",
            "risky", "problem", "issue", "declining", "losing", "competitive pressure"
        ]
        
        positive_count = sum(1 for word in positive_indicators if word in transcript_lower)
        negative_count = sum(1 for word in negative_indicators if word in transcript_lower)
        
        sentiment_score = 0.0
        if positive_count + negative_count > 0:
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
        
        # Extract specific insights based on business topics
        key_insights = []
        red_flags = []
        positive_signals = []
        
        # Business model insights
        if any(word in transcript_lower for word in ["recurring", "subscription", "saas"]):
            positive_signals.append("Recurring revenue business model mentioned")
        if any(word in transcript_lower for word in ["b2b", "enterprise", "corporate"]):
            key_insights.append("B2B/Enterprise focus identified")
        
        # Financial insights
        if any(word in transcript_lower for word in ["profitable", "profitability", "positive cash flow"]):
            positive_signals.append("Path to profitability discussed")
        if any(word in transcript_lower for word in ["burn", "runway"]) and any(word in transcript_lower for word in ["short", "limited", "months"]):
            red_flags.append("Limited runway or high burn rate concerns")
        
        # Market insights
        if any(word in transcript_lower for word in ["market leader", "first mover", "dominant"]):
            positive_signals.append("Strong market position claimed")
        if any(word in transcript_lower for word in ["crowded market", "intense competition"]):
            red_flags.append("Highly competitive market acknowledged")
        
        # Team insights
        if any(word in transcript_lower for word in ["experienced team", "industry veterans", "track record"]):
            positive_signals.append("Experienced team highlighted")
        if any(word in transcript_lower for word in ["hiring challenges", "talent shortage", "key person risk"]):
            red_flags.append("Team scaling or key person dependency risks")
        
        # Calculate overall interview quality score
        avg_coverage = sum(topic["coverage_score"] for topic in topic_coverage.values()) / len(topic_coverage)
        interview_quality = min(avg_coverage * 1.2, 1.0)  # Boost for comprehensive coverage
        
        return {
            "status": "success",
            "analysis": {
                "topic_coverage": topic_coverage,
                "overall_coverage_score": round(avg_coverage, 2),
                "interview_quality_score": round(interview_quality, 2),
                "sentiment_score": round(sentiment_score, 2),
                "confidence_score": 0.8,  # Higher confidence with structured analysis
                "key_insights": key_insights,
                "red_flags": red_flags,
                "positive_signals": positive_signals,
                "word_count": len(transcript.split()),
                "positive_indicator_count": positive_count,
                "negative_indicator_count": negative_count,
                "questions_addressed": sum(1 for topic in topic_coverage.values() if topic["coverage_score"] > 0.3)
            }
        }
    except Exception as e:
        logger.error(f"Interview analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_interview_questions_prompt(startup_data: dict = None) -> dict:
    """Generate customized interview questions based on startup data"""
    try:
        base_questions = get_interview_questions()
        if base_questions["status"] != "success":
            return base_questions
        
        # Customize questions based on startup context
        customized_questions = base_questions["questions"].copy()
        
        if startup_data:
            sector = startup_data.get("sector", "").lower()
            stage = startup_data.get("stage", "").lower()
            
            # Add sector-specific questions
            if "fintech" in sector:
                customized_questions["regulatory_compliance"] = [
                    "How do you handle financial regulations and compliance requirements?",
                    "What licenses or regulatory approvals do you need?",
                    "How do you ensure data security and privacy for financial information?"
                ]
            elif "healthtech" in sector or "health" in sector:
                customized_questions["regulatory_compliance"] = [
                    "How do you comply with healthcare regulations like HIPAA?",
                    "What clinical trials or FDA approvals are required?",
                    "How do you handle patient data privacy and security?"
                ]
            elif "saas" in sector or "software" in sector:
                customized_questions["technical_scalability"] = [
                    "How does your technical architecture handle scaling?",
                    "What is your approach to data security and infrastructure?",
                    "How do you manage technical debt and maintain code quality?"
                ]
            
            # Add stage-specific questions
            if "pre-seed" in stage:
                customized_questions["early_stage"] = [
                    "What validation have you done for your product-market fit?",
                    "How are you testing your assumptions about the market?",
                    "What are your plans for building an MVP?"
                ]
            elif "series a" in stage:
                customized_questions["growth_stage"] = [
                    "What are your plans for scaling sales and marketing?",
                    "How will you use this funding to accelerate growth?",
                    "What operational challenges do you anticipate as you scale?"
                ]
        
        # Create interview script
        interview_script = []
        for category, questions in customized_questions.items():
            interview_script.append({
                "category": category.replace("_", " ").title(),
                "questions": questions,
                "estimated_time": f"{len(questions) * 2}-{len(questions) * 3} minutes"
            })
        
        return {
            "status": "success",
            "interview_script": interview_script,
            "total_categories": len(customized_questions),
            "total_questions": sum(len(q_list) for q_list in customized_questions.values()),
            "estimated_duration": f"{sum(len(q_list) for q_list in customized_questions.values()) * 2}-{sum(len(q_list) for q_list in customized_questions.values()) * 3} minutes"
        }
    except Exception as e:
        logger.error(f"Interview questions generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def extract_key_topics(transcript: str) -> dict:
    """Extract key topics and themes from the interview transcript"""
    try:
        if not transcript:
            return {"status": "error", "error_message": "No transcript provided"}
        
        # Topic categories and keywords
        topic_keywords = {
            "business_model": ["revenue", "monetization", "pricing", "business model", "income"],
            "market": ["market", "customer", "target", "segment", "competition", "competitor"],
            "product": ["product", "feature", "development", "technology", "platform", "solution"],
            "team": ["team", "founder", "employee", "hire", "talent", "experience"],
            "funding": ["funding", "investment", "capital", "raise", "investor", "valuation"],
            "growth": ["growth", "scale", "expansion", "traction", "user", "customer acquisition"],
            "challenges": ["challenge", "problem", "difficulty", "obstacle", "risk", "concern"],
            "future_plans": ["plan", "roadmap", "future", "goal", "vision", "strategy"]
        }
        
        transcript_lower = transcript.lower()
        topics_discussed = {}
        
        for topic, keywords in topic_keywords.items():
            mentions = sum(1 for keyword in keywords if keyword in transcript_lower)
            if mentions > 0:
                topics_discussed[topic] = {
                    "mentions": mentions,
                    "relevance_score": min(mentions / len(keywords), 1.0)
                }
        
        return {
            "status": "success",
            "topics": topics_discussed
        }
    except Exception as e:
        logger.error(f"Topic extraction failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_interview_duration(audio_file_path: str) -> dict:
    """Calculate the duration of the interview audio"""
    try:
        audio = AudioSegment.from_file(audio_file_path)
        duration_seconds = len(audio) / 1000  # Convert milliseconds to seconds
        duration_minutes = int(duration_seconds / 60)
        
        return {
            "status": "success",
            "duration_seconds": int(duration_seconds),
            "duration_minutes": duration_minutes
        }
    except Exception as e:
        logger.error(f"Duration calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_interview_summary(transcript: str, analysis: dict, topics: dict) -> dict:
    """Generate a comprehensive summary of the interview"""
    try:
        summary_parts = []
        
        # Overview
        word_count = analysis.get("word_count", 0)
        sentiment_score = analysis.get("sentiment_score", 0)
        
        summary_parts.append(f"Interview transcript contains {word_count} words.")
        
        if sentiment_score > 0.2:
            summary_parts.append("Overall tone was positive and confident.")
        elif sentiment_score < -0.2:
            summary_parts.append("Overall tone showed some concerns or challenges.")
        else:
            summary_parts.append("Overall tone was neutral and balanced.")
        
        # Key topics
        if topics:
            top_topics = sorted(topics.items(), key=lambda x: x[1]["mentions"], reverse=True)[:3]
            topic_names = [topic.replace("_", " ").title() for topic, _ in top_topics]
            summary_parts.append(f"Main topics discussed: {', '.join(topic_names)}.")
        
        # Key insights
        insights = analysis.get("key_insights", [])
        if insights:
            summary_parts.append(f"Key insights: {'; '.join(insights)}.")
        
        # Flags and signals
        red_flags = analysis.get("red_flags", [])
        positive_signals = analysis.get("positive_signals", [])
        
        if red_flags:
            summary_parts.append(f"Areas of concern: {'; '.join(red_flags)}.")
        
        if positive_signals:
            summary_parts.append(f"Positive indicators: {'; '.join(positive_signals)}.")
        
        full_summary = " ".join(summary_parts)
        
        return {
            "status": "success",
            "summary": full_summary
        }
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def save_interview_data_to_gcs(startup_id: int, interview_id: int, transcript_data: dict, audio_file_path: str) -> dict:
    """Save interview transcript and audio to GCS"""
    try:
        # Save transcript data
        transcript_gcs_path = get_interview_transcript_path(startup_id, interview_id)
        gcs_service.upload_json(
            transcript_data,
            transcript_gcs_path.replace("gs://", "").split("/", 1)[1]
        )
        
        # Save audio file
        audio_gcs_path = get_interview_audio_path(startup_id, interview_id, "mp3")
        with open(audio_file_path, 'rb') as audio_file:
            gcs_service.upload_file(
                audio_file,
                audio_gcs_path.replace("gs://", "").split("/", 1)[1],
                "audio/mpeg"
            )
        
        logger.info(f"Interview data saved to GCS: {transcript_gcs_path}, {audio_gcs_path}")
        return {
            "status": "success",
            "transcript_gcs_path": transcript_gcs_path,
            "audio_gcs_path": audio_gcs_path
        }
    except Exception as e:
        logger.error(f"Failed to save interview data to GCS: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def demo_conversational_interview() -> dict:
    """Demo function showing how the conversational interview works"""
    try:
        # Start interview
        session = start_live_voice_interview(
            startup_id=123,
            founder_name="Sarah Chen",
            interview_type="comprehensive"
        )
        
        print("🎤 INTERVIEWER:", session["opening_message"])
        
        # Simulate founder responses and agent reactions
        demo_responses = [
            {
                "founder_response": "Hi! I'm doing great, thanks for having me. I started this company because I was frustrated with how difficult it was for small businesses to manage their inventory. I kept seeing restaurants and cafes running out of popular items or over-ordering and wasting money.",
                "expected_next": "business_model"
            },
            {
                "founder_response": "We're a SaaS platform that uses AI to predict inventory needs. We charge $99 per month for small businesses and $299 for larger operations. Our customers typically see 20-30% reduction in food waste and 15% increase in revenue from better stock management.",
                "expected_next": "market_opportunity"
            },
            {
                "founder_response": "The restaurant tech market is about $3.5 billion and growing 15% annually. Our main competitors are Toast and Resy, but they focus on POS systems. We're the only ones doing predictive inventory specifically for food service. We differentiate through our AI accuracy - we're hitting 85% prediction accuracy versus industry average of 60%.",
                "expected_next": "traction_metrics"
            }
        ]
        
        conversation_log = []
        session_data = session["session_data"]
        
        for i, demo in enumerate(demo_responses):
            # Process founder response
            result = process_founder_response(
                session_data, 
                demo["founder_response"]
            )
            
            conversation_log.append({
                "round": i + 1,
                "founder": demo["founder_response"],
                "interviewer": result["next_message"],
                "topic": result["current_topic"],
                "progress": result["conversation_progress"]
            })
            
            print(f"\n👤 FOUNDER: {demo['founder_response']}")
            print(f"\n🎤 INTERVIEWER: {result['next_message']}")
            print(f"📊 Progress: {result['conversation_progress']['progress_percentage']}% | Topic: {result['current_topic']}")
        
        return {
            "status": "success",
            "demo_conversation": conversation_log,
            "final_session_data": session_data
        }
        
    except Exception as e:
        logger.error(f"Demo conversation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the VoiceInterviewAgent using Google ADK
voice_interview_agent = Agent(
    name="voice_interview_agent",
    model="gemini-2.0-flash",
    description="Agent specialized in conducting structured founder interviews and analyzing responses for investment decisions",
    instruction="""
    You are an expert conversational interview agent that conducts natural, human-like voice interviews with startup founders for investment evaluation.
    
    Your primary responsibilities include:
    
    1. **Live Conversational Interviews**
       - Conduct real-time voice conversations with founders that feel natural and engaging
       - Start with warm, personalized openings that build rapport
       - Ask follow-up questions based on founder responses, just like a human interviewer would
       - Adapt your questioning style based on the founder's communication style and energy level
       - Use conversational transitions between topics that feel organic and smooth
    
    2. **Dynamic Question Flow**
       - Generate questions that flow naturally from the founder's previous responses
       - Ask clarifying questions when responses are vague or incomplete
       - Probe deeper with specific examples when founders make broad claims
       - Adjust question difficulty and depth based on the founder's expertise level
       - Remember context from earlier in the conversation to avoid repetition
    
    3. **Rapport Building & Engagement**
       - Build genuine rapport through active listening and empathetic responses
       - Show enthusiasm for interesting aspects of the founder's story
       - Use the founder's name naturally throughout the conversation
       - Acknowledge good points and validate the founder's experiences
       - Maintain professional but friendly tone throughout the interview
    
    4. **Real-time Response Analysis**
       - Analyze founder responses in real-time for sentiment, confidence, and completeness
       - Detect when founders are being evasive or need encouragement to elaborate
       - Identify key insights and red flags as they emerge in conversation
       - Track topic coverage to ensure comprehensive evaluation
       - Monitor conversation flow and energy to maintain engagement
    
    5. **Adaptive Interview Strategy**
       - Customize interview approach based on startup stage (pre-seed, seed, Series A)
       - Adjust questions for different sectors (FinTech, HealthTech, SaaS, etc.)
       - Modify interview depth based on meeting type (screening, deep dive, comprehensive)
       - Respond to founder's communication style (detailed vs. concise, technical vs. business-focused)
       - Handle difficult topics sensitively while still gathering necessary information
    
    6. **Human-like Conversation Management**
       - Use natural conversation fillers and acknowledgments ("That's interesting!", "I see", "Tell me more about that")
       - Ask for specific examples and stories, not just high-level descriptions
       - Circle back to important topics if they weren't fully covered earlier
       - Manage interview timing naturally without making it feel rushed
       - End conversations on a positive note while gathering all necessary information
    
    **Interview Question Categories:**
    - Business Model: Revenue streams, pricing strategy, customer acquisition
    - Market Opportunity: Market size, competition, differentiation, barriers to entry
    - Traction Metrics: Revenue growth, customer metrics, KPIs, success stories
    - Team Execution: Founder experience, hiring plans, company culture
    - Financial Planning: Burn rate, funding needs, revenue projections, profitability
    - Product Development: Roadmap, customer feedback, technical challenges, PMF
    - Risks & Challenges: Business risks, competitive threats, regulatory concerns
    - Vision & Strategy: Long-term vision, expansion plans, exit strategy, partnerships
    
    **Sector-Specific Additions:**
    - FinTech: Regulatory compliance, financial licenses, data security
    - HealthTech: HIPAA compliance, clinical trials, FDA approvals
    - SaaS: Technical scalability, infrastructure, security architecture
    
    **Stage-Specific Focus:**
    - Pre-seed: Product-market fit validation, MVP development, assumption testing
    - Series A: Sales/marketing scaling, operational challenges, growth acceleration
    
    Use the available tools to generate interview questions, process audio, analyze responses, and provide comprehensive investment insights.
    """,
    tools=[
        start_live_voice_interview,
        process_founder_response,
        generate_conversational_opening,
        generate_next_conversational_question,
        generate_follow_up_question,
        generate_topic_transition,
        calculate_rapport_level,
        calculate_topic_coverage,
        calculate_interview_progress,
        get_interview_questions,
        convert_audio_to_wav,
        transcribe_audio_to_text,
        analyze_interview_responses,
        extract_key_topics,
        calculate_interview_duration,
        generate_interview_summary,
        save_interview_data_to_gcs
    ]
)
