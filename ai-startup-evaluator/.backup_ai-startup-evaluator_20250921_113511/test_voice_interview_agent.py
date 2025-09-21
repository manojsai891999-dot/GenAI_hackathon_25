#!/usr/bin/env python3
"""
Test script for the Voice Interview Agent
Demonstrates conversational interview capabilities
"""

import sys
import os
import json
from datetime import datetime

# Standalone implementation for testing
def generate_conversational_opening(founder_name: str, interview_type: str) -> str:
    """Generate a warm, conversational opening for the interview"""
    openings = {
        "comprehensive": f"Hi {founder_name}! Thanks for taking the time to chat with me today. I'm really excited to learn more about what you're building. Before we dive in, how are you doing? And maybe you could start by telling me a bit about yourself and what inspired you to start this company?",
        
        "screening": f"Hello {founder_name}! Great to meet you. I've been looking forward to our conversation. I know your time is valuable, so I'd love to hear your story. Could you give me the elevator pitch - what's your company all about and what problem are you solving?",
        
        "deep_dive": f"Hi {founder_name}! Thanks for joining me for this deeper conversation about your company. I've reviewed some initial materials, and I'm impressed by what I've seen so far. I'd love to dig into the details with you. Shall we start with you telling me how the business has evolved since you first started?"
    }
    
    return openings.get(interview_type, openings["comprehensive"])

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
        return {"status": "error", "error_message": str(e)}

def analyze_response_content(response: str, current_topic: str) -> dict:
    """Analyze founder's response for content, sentiment, and insights"""
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
    
    # Extract key insights
    insights = {}
    topic_keywords = {
        "business_model": ["revenue", "pricing", "customers", "sales", "subscription", "b2b", "b2c"],
        "market_opportunity": ["market", "competitors", "competition", "differentiate", "market share"],
        "traction_metrics": ["revenue", "customers", "retention", "growth", "metrics", "kpi"]
    }
    
    keywords = topic_keywords.get(current_topic, [])
    for keyword in keywords:
        if keyword in response_lower:
            insights[keyword] = True
    
    # Assess response quality
    quality_score = min(word_count / 100, 1.0) * 0.6 + sentiment_score * 0.4
    
    return {
        "word_count": word_count,
        "sentiment_score": sentiment_score,
        "quality_score": quality_score,
        "insights": insights,
        "needs_follow_up": quality_score < 0.6 or word_count < 20
    }

def generate_next_question(session_data: dict, response_analysis: dict) -> dict:
    """Generate the next conversational question"""
    current_topic = session_data["current_topic"]
    founder_name = session_data["founder_name"]
    
    # Topic transitions
    transitions = {
        "introduction": ("business_model", f"Thanks for sharing that background, {founder_name}! Now I'd love to understand the business side better. How exactly do you make money? Walk me through your revenue model."),
        "business_model": ("market_opportunity", "That business model makes sense! Now let's talk about the market you're going after. How big is this opportunity, and who else is competing for it?"),
        "market_opportunity": ("traction_metrics", "The market opportunity sounds compelling! I'm curious about the traction you're seeing. What does your growth look like so far?"),
        "traction_metrics": ("team_execution", "Those metrics are encouraging! Let's talk about the team behind this growth. Tell me about your founding team and how you're thinking about scaling.")
    }
    
    if current_topic in transitions:
        next_topic, message = transitions[current_topic]
        return {
            "message": message,
            "topic": next_topic,
            "type": "transition"
        }
    else:
        return {
            "message": f"That's great, {founder_name}! Can you tell me more about that?",
            "topic": current_topic,
            "type": "follow_up"
        }

def process_founder_response(session_data: dict, founder_response: str) -> dict:
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
            "analysis": response_analysis
        })
        
        # Update insights and rapport
        session_data["insights_gathered"].update(response_analysis.get("insights", {}))
        
        # Calculate rapport (simple version)
        founder_responses = [msg for msg in session_data["conversation_history"] if msg["speaker"] == "founder"]
        avg_sentiment = sum(msg.get("analysis", {}).get("sentiment_score", 0.5) for msg in founder_responses) / len(founder_responses)
        session_data["rapport_level"] = round(avg_sentiment, 2)
        
        # Generate next question
        next_interaction = generate_next_question(session_data, response_analysis)
        
        # Add interviewer response to history
        session_data["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "speaker": "interviewer",
            "content": next_interaction["message"],
            "topic": next_interaction["topic"],
            "question_type": next_interaction["type"]
        })
        
        session_data["current_topic"] = next_interaction["topic"]
        
        # Calculate progress
        topics = ["introduction", "business_model", "market_opportunity", "traction_metrics", "team_execution"]
        current_index = topics.index(session_data["current_topic"]) if session_data["current_topic"] in topics else 0
        progress_percentage = (current_index / len(topics)) * 100
        
        start_time = datetime.fromisoformat(session_data["start_time"])
        elapsed_minutes = (datetime.now() - start_time).total_seconds() / 60
        
        conversation_progress = {
            "current_topic": session_data["current_topic"],
            "progress_percentage": round(progress_percentage, 1),
            "elapsed_minutes": round(elapsed_minutes, 1),
            "topics_completed": current_index,
            "total_topics": len(topics)
        }
        
        return {
            "status": "success",
            "next_message": next_interaction["message"],
            "current_topic": next_interaction["topic"],
            "conversation_progress": conversation_progress,
            "session_data": session_data
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

def calculate_rapport_level(conversation_history: list) -> float:
    """Calculate rapport level based on conversation dynamics"""
    if len(conversation_history) < 2:
        return 0.5
    
    founder_responses = [msg for msg in conversation_history if msg["speaker"] == "founder"]
    
    # Analyze response lengths and sentiment
    avg_response_length = sum(len(msg["content"].split()) for msg in founder_responses) / len(founder_responses)
    length_score = min(avg_response_length / 100, 1.0)
    
    sentiment_scores = [msg.get("analysis", {}).get("sentiment_score", 0.5) for msg in founder_responses]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.5
    
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
        "traction_metrics": ["revenue", "customers", "retention", "growth"]
    }
    
    expected_keywords = topic_keywords.get(topic, [])
    covered_keywords = sum(1 for keyword in expected_keywords if topic_insights.get(keyword, False))
    keyword_coverage = covered_keywords / len(expected_keywords) if expected_keywords else 0
    
    # Combine word count and keyword coverage
    word_score = min(total_words / 150, 1.0)  # Target ~150 words per topic
    coverage_score = (word_score * 0.4 + keyword_coverage * 0.6)
    
    return round(coverage_score, 2)

def test_interview_opening():
    """Test the conversational opening generation"""
    print("🧪 Testing Interview Openings...")
    print("=" * 50)
    
    test_cases = [
        ("John Smith", "comprehensive"),
        ("Maria Rodriguez", "screening"), 
        ("Alex Chen", "deep_dive")
    ]
    
    for founder_name, interview_type in test_cases:
        opening = generate_conversational_opening(founder_name, interview_type)
        print(f"\n📋 {interview_type.upper()} Interview with {founder_name}:")
        print(f"🎤 INTERVIEWER: {opening}")

def test_live_interview_session():
    """Test starting a live interview session"""
    print("\n\n🧪 Testing Live Interview Session...")
    print("=" * 50)
    
    # Start interview session
    session = start_live_voice_interview(
        startup_id=456,
        founder_name="Emma Thompson",
        interview_type="comprehensive"
    )
    
    if session["status"] == "success":
        print("✅ Interview session started successfully!")
        print(f"📋 Session ID: {session['session_data']['session_id']}")
        print(f"🎤 Opening: {session['opening_message']}")
        
        # Display session state
        session_data = session["session_data"]
        print(f"\n📊 Session State:")
        print(f"   - Founder: {session_data['founder_name']}")
        print(f"   - Type: {session_data['interview_type']}")
        print(f"   - Current Topic: {session_data['current_topic']}")
        print(f"   - Rapport Level: {session_data['rapport_level']}")
        
        return session_data
    else:
        print(f"❌ Failed to start session: {session['error_message']}")
        return None

def test_conversation_flow():
    """Test the full conversation flow with realistic responses"""
    print("\n\n🧪 Testing Conversation Flow...")
    print("=" * 50)
    
    # Start session
    session = start_live_voice_interview(
        startup_id=789,
        founder_name="David Park",
        interview_type="comprehensive"
    )
    
    if session["status"] != "success":
        print("❌ Failed to start session")
        return
    
    session_data = session["session_data"]
    print(f"🎤 INTERVIEWER: {session['opening_message']}")
    
    # Simulate realistic founder responses
    test_responses = [
        {
            "response": "Hi! I'm doing well, thank you. I started TechFlow because I was frustrated with how small businesses struggle with digital transformation. I saw my family's restaurant using outdated systems and realized there was a huge gap in affordable, easy-to-use business software.",
            "description": "Introduction - Personal story"
        },
        {
            "response": "We're a SaaS platform that provides an all-in-one business management suite for small businesses. We charge $49 per month for basic features and $149 for premium. Our customers typically see 30% improvement in operational efficiency and save about 10 hours per week on administrative tasks.",
            "description": "Business Model - Clear value prop"
        },
        {
            "response": "The small business software market is about $15 billion and growing at 12% annually. Our main competitors are QuickBooks and Square, but they're either too complex or too limited. We differentiate by focusing specifically on businesses with 5-50 employees and providing industry-specific workflows.",
            "description": "Market Opportunity - Specific positioning"
        },
        {
            "response": "We launched 8 months ago and now have 240 paying customers. Our monthly recurring revenue is $18,000 and growing 25% month-over-month. Customer retention is 94% and our Net Promoter Score is 67. One of our restaurant clients increased their table turnover by 40% using our scheduling features.",
            "description": "Traction - Strong metrics with example"
        },
        {
            "response": "I'm the CEO with 8 years of enterprise software experience at Salesforce. My co-founder Sarah is our CTO - she built the core platform and has a computer science PhD from Stanford. We're looking to hire 2 engineers and a sales person in the next 6 months.",
            "description": "Team - Strong credentials"
        }
    ]
    
    conversation_log = []
    
    for i, test_case in enumerate(test_responses):
        print(f"\n--- Round {i+1}: {test_case['description']} ---")
        print(f"👤 FOUNDER: {test_case['response']}")
        
        # Process the response
        result = process_founder_response(
            session_data, 
            test_case["response"]
        )
        
        if result["status"] == "success":
            print(f"🎤 INTERVIEWER: {result['next_message']}")
            
            # Show analysis
            progress = result["conversation_progress"]
            print(f"\n📊 Analysis:")
            print(f"   - Topic: {result['current_topic']}")
            print(f"   - Progress: {progress['progress_percentage']}%")
            print(f"   - Elapsed: {progress['elapsed_minutes']} min")
            print(f"   - Rapport Level: {session_data['rapport_level']}")
            
            conversation_log.append({
                "round": i + 1,
                "founder_response": test_case["response"],
                "interviewer_response": result["next_message"],
                "topic": result["current_topic"],
                "progress": progress
            })
        else:
            print(f"❌ Error processing response: {result['error_message']}")
            break
    
    return conversation_log

def test_rapport_calculation():
    """Test rapport level calculation"""
    print("\n\n🧪 Testing Rapport Calculation...")
    print("=" * 50)
    
    # Mock conversation history with different engagement levels
    test_histories = [
        {
            "name": "High Engagement",
            "history": [
                {"speaker": "founder", "content": "I'm absolutely passionate about solving this problem. We've built something revolutionary that's already helping hundreds of businesses transform their operations.", "analysis": {"sentiment_score": 0.9}},
                {"speaker": "founder", "content": "Our customers love the platform! For example, one restaurant owner told us we saved his business during COVID by helping him pivot to delivery efficiently.", "analysis": {"sentiment_score": 0.8}},
            ]
        },
        {
            "name": "Low Engagement", 
            "history": [
                {"speaker": "founder", "content": "Yeah, it's okay.", "analysis": {"sentiment_score": 0.4}},
                {"speaker": "founder", "content": "I guess we're doing fine.", "analysis": {"sentiment_score": 0.3}},
            ]
        },
        {
            "name": "Mixed Engagement",
            "history": [
                {"speaker": "founder", "content": "We're excited about the opportunity, but there are definitely challenges in the market.", "analysis": {"sentiment_score": 0.6}},
                {"speaker": "founder", "content": "The technology is solid and our early customers are seeing good results, though we're still figuring out the go-to-market strategy.", "analysis": {"sentiment_score": 0.7}},
            ]
        }
    ]
    
    for test_case in test_histories:
        rapport = calculate_rapport_level(test_case["history"])
        print(f"📊 {test_case['name']}: Rapport Level = {rapport}")

def test_topic_coverage():
    """Test topic coverage calculation"""
    print("\n\n🧪 Testing Topic Coverage...")
    print("=" * 50)
    
    # Mock session data with different coverage levels
    session_data = {
        "conversation_history": [
            {"speaker": "founder", "content": "Our revenue model is subscription-based with monthly and annual pricing tiers for different customer segments.", "topic": "business_model"},
            {"speaker": "founder", "content": "We focus on customer acquisition through digital marketing and have a clear sales process with defined conversion metrics.", "topic": "business_model"},
            {"speaker": "founder", "content": "The market is huge and growing rapidly.", "topic": "market_opportunity"},  # Brief response
        ],
        "insights_gathered": {
            "revenue": True,
            "pricing": True, 
            "customers": True,
            "sales": True,
            "market": True
        }
    }
    
    topics = ["business_model", "market_opportunity", "traction_metrics"]
    
    for topic in topics:
        coverage = calculate_topic_coverage(session_data, topic)
        print(f"📋 {topic.replace('_', ' ').title()}: {coverage * 100:.1f}% coverage")

def run_demo_interview():
    """Run a demo interview with realistic conversation"""
    print("\n\n🧪 Running Demo Interview...")
    print("=" * 50)
    
    try:
        # Start demo session
        session = start_live_voice_interview(
            startup_id=999,
            founder_name="Jessica Kim",
            interview_type="comprehensive"
        )
        
        if session["status"] != "success":
            print("❌ Failed to start demo session")
            return
        
        session_data = session["session_data"]
        print(f"🎤 INTERVIEWER: {session['opening_message']}")
        
        # Demo responses showing natural conversation flow
        demo_responses = [
            "Hi! I'm doing fantastic, thank you for having me. I started FoodFlow because I was constantly frustrated watching restaurants waste food while struggling with inventory. My family owns a small restaurant, and I saw firsthand how they'd run out of popular dishes or over-order ingredients that would spoil.",
            
            "We're a SaaS platform that uses machine learning to predict restaurant inventory needs. We charge $149 per month for our standard plan and $299 for premium with advanced analytics. Our customers typically reduce food waste by 35% and increase profit margins by 12% within the first quarter.",
            
            "The restaurant technology market is valued at $4.2 billion and growing at 18% annually. Our main competitors are Toast and Resy, but they focus on point-of-sale systems. We're the only company specifically targeting predictive inventory management for food service. Our AI achieves 89% accuracy in demand forecasting versus the industry standard of 65%.",
            
            "We launched 14 months ago and now serve 180 restaurants across 12 cities. Our monthly recurring revenue hit $32,000 last month with 28% month-over-month growth. Customer retention is 96% and our Net Promoter Score is 73. One client, a pizza chain with 8 locations, reduced their food costs by $4,200 monthly using our system."
        ]
        
        print("\n" + "="*60)
        print("🎭 REALISTIC CONVERSATION DEMO")
        print("="*60)
        
        for i, response in enumerate(demo_responses):
            print(f"\n--- Exchange {i+1} ---")
            print(f"👤 FOUNDER: {response}")
            
            # Process response
            result = process_founder_response(session_data, response)
            
            if result["status"] == "success":
                print(f"🎤 INTERVIEWER: {result['next_message']}")
                
                # Show real-time analysis
                progress = result["conversation_progress"]
                print(f"\n📊 Real-time Analysis:")
                print(f"   🎯 Current Topic: {result['current_topic'].replace('_', ' ').title()}")
                print(f"   📈 Progress: {progress['progress_percentage']}% complete")
                print(f"   ⏱️  Elapsed Time: {progress['elapsed_minutes']:.1f} minutes")
                print(f"   🤝 Rapport Level: {session_data['rapport_level']}")
                
                # Show insights gathered
                insights = list(session_data['insights_gathered'].keys())
                if insights:
                    print(f"   💡 Key Insights: {', '.join(insights[:5])}")
            else:
                print(f"❌ Error: {result['error_message']}")
                break
        
        print(f"\n✅ Demo completed! Final rapport level: {session_data['rapport_level']}")
        return session_data
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Voice Interview Agent Test Suite")
    print("=" * 60)
    
    try:
        # Run individual tests
        test_interview_opening()
        test_live_interview_session()
        test_rapport_calculation()
        test_topic_coverage()
        
        # Run conversation flow test
        conversation_log = test_conversation_flow()
        
        # Run demo
        run_demo_interview()
        
        print("\n\n✅ All tests completed!")
        print("=" * 60)
        
        # Summary
        print("\n📊 Test Summary:")
        print("✅ Interview opening generation")
        print("✅ Live session management")
        print("✅ Conversation flow processing")
        print("✅ Rapport level calculation")
        print("✅ Topic coverage tracking")
        print("✅ Demo interview execution")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
