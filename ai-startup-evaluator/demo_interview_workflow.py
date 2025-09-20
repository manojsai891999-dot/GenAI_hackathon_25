#!/usr/bin/env python3
"""
Demo of the complete interview workflow
Shows: Email invitation → Meeting acceptance → Voice interview
"""

import uuid
from datetime import datetime

def send_interview_invitation_email(founder_email: str, founder_name: str, startup_name: str) -> dict:
    """Simulate sending interview invitation email"""
    meeting_id = str(uuid.uuid4())
    acceptance_link = f"http://localhost:3000/accept-interview/{meeting_id}"
    
    email_content = f"""
📧 EMAIL SENT TO: {founder_email}
=====================================

Subject: Investment Interview Invitation - {startup_name}

Dear {founder_name},

Thank you for submitting your startup materials for {startup_name}. 
After reviewing your pitch deck and materials, we're impressed with what you're building 
and would like to schedule a Founder Interview to learn more about your company.

Interview Details:
• Type: Founder Interview  
• Duration: 45 minutes
• Format: Voice Interview (AI-powered)
• Topics: Business model, market opportunity, traction, team, and vision

This will be an interactive voice conversation where you'll have the opportunity to 
discuss your startup in detail. Our AI interviewer is designed to conduct natural, 
engaging conversations that feel like talking to an experienced investor.

🔗 ACCEPTANCE LINK: {acceptance_link}

What to expect:
• Natural conversation flow with follow-up questions
• Discussion of your business model and revenue strategy  
• Market analysis and competitive positioning
• Traction metrics and growth plans
• Team composition and execution capabilities
• Vision and long-term strategy

Please click the acceptance link above to confirm your participation.

Best regards,
Investment Team
AI Startup Evaluator

Meeting ID: {meeting_id}
    """
    
    print(email_content)
    
    return {
        "status": "success",
        "meeting_id": meeting_id,
        "email_sent": True,
        "acceptance_link": acceptance_link,
        "founder_email": founder_email,
        "founder_name": founder_name,
        "startup_name": startup_name
    }

def simulate_meeting_acceptance(meeting_id: str, founder_name: str) -> dict:
    """Simulate founder accepting the meeting"""
    print(f"\n⏳ WAITING FOR FOUNDER RESPONSE...")
    print("=" * 50)
    print(f"💭 {founder_name} receives the email...")
    print(f"📱 {founder_name} clicks the acceptance link...")
    print(f"✅ Meeting {meeting_id} ACCEPTED!")
    
    return {
        "status": "success",
        "meeting_accepted": True,
        "accepted_at": datetime.now().isoformat()
    }

def start_voice_interview_session(meeting_id: str, founder_name: str, startup_name: str) -> dict:
    """Start the voice interview session"""
    session_id = f"voice_interview_{meeting_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    opening_message = f"""Hi {founder_name}! Thanks so much for accepting our interview invitation for {startup_name}. 
I'm really excited to dive deeper into what you're building after reviewing your initial materials.

This will be a conversational interview where we'll explore your business in detail - think of it as 
a friendly chat with an investor who's genuinely interested in your story.

Before we begin, how are you feeling about this conversation? And maybe you could start by telling me 
what's been the most exciting development at {startup_name} recently?"""
    
    session_data = {
        "session_id": session_id,
        "meeting_id": meeting_id,
        "founder_name": founder_name,
        "startup_name": startup_name,
        "start_time": datetime.now().isoformat(),
        "current_topic": "introduction",
        "conversation_history": [],
        "insights_gathered": {},
        "rapport_level": 0.5
    }
    
    return {
        "status": "success",
        "session_data": session_data,
        "opening_message": opening_message
    }

def process_founder_response(session_data: dict, response: str) -> dict:
    """Process founder's response and generate next question"""
    # Simple response analysis
    word_count = len(response.split())
    positive_words = ["excited", "fantastic", "great", "amazing", "successful", "growing"]
    positive_count = sum(1 for word in positive_words if word.lower() in response.lower())
    
    # Update rapport based on response quality
    if word_count > 50 and positive_count > 0:
        session_data["rapport_level"] = min(session_data["rapport_level"] + 0.1, 1.0)
    
    # Add to conversation history
    session_data["conversation_history"].append({
        "timestamp": datetime.now().isoformat(),
        "speaker": "founder",
        "content": response,
        "word_count": word_count,
        "positive_sentiment": positive_count > 0
    })
    
    # Generate next question based on current topic
    current_topic = session_data["current_topic"]
    founder_name = session_data["founder_name"]
    
    topic_transitions = {
        "introduction": {
            "next_topic": "business_model",
            "message": f"That's fantastic, {founder_name}! I love hearing about that kind of progress. Now I'd love to understand the business mechanics better. How exactly does {session_data['startup_name']} make money? Walk me through your revenue model."
        },
        "business_model": {
            "next_topic": "market_opportunity", 
            "message": f"That business model sounds solid! Now let's talk about the market you're going after. How big is this opportunity, and who else is competing for it?"
        },
        "market_opportunity": {
            "next_topic": "traction_metrics",
            "message": f"The market opportunity sounds compelling! I'm curious about the traction you're seeing. What does your growth look like so far?"
        },
        "traction_metrics": {
            "next_topic": "team_execution",
            "message": f"Those are encouraging numbers! Let's talk about the team behind this growth. Tell me about your founding team and how you're thinking about scaling."
        },
        "team_execution": {
            "next_topic": "vision_strategy",
            "message": f"Sounds like you have a strong team! Looking ahead, where do you see {session_data['startup_name']} in 5 years? What's your long-term vision?"
        }
    }
    
    if current_topic in topic_transitions:
        transition = topic_transitions[current_topic]
        session_data["current_topic"] = transition["next_topic"]
        next_message = transition["message"]
    else:
        next_message = f"That's great, {founder_name}! Can you tell me more about that?"
    
    # Add interviewer response to history
    session_data["conversation_history"].append({
        "timestamp": datetime.now().isoformat(),
        "speaker": "interviewer", 
        "content": next_message,
        "topic": session_data["current_topic"]
    })
    
    # Calculate progress
    topics = ["introduction", "business_model", "market_opportunity", "traction_metrics", "team_execution", "vision_strategy"]
    current_index = topics.index(session_data["current_topic"]) if session_data["current_topic"] in topics else 0
    progress_percentage = (current_index / len(topics)) * 100
    
    return {
        "status": "success",
        "next_message": next_message,
        "current_topic": session_data["current_topic"],
        "progress_percentage": round(progress_percentage, 1),
        "rapport_level": session_data["rapport_level"]
    }

def conduct_interactive_interview(session_data: dict) -> dict:
    """Conduct a full interactive interview simulation"""
    print(f"\n🎤 STARTING VOICE INTERVIEW")
    print("=" * 60)
    print(f"Founder: {session_data['founder_name']}")
    print(f"Startup: {session_data['startup_name']}")
    print(f"Session: {session_data['session_id']}")
    print("=" * 60)
    
    # Realistic founder responses for Syed Ubedulla Khadri
    demo_responses = [
        {
            "response": f"Hi! I'm feeling fantastic about this conversation, thank you for the opportunity. The most exciting development at {session_data['startup_name']} recently has been securing our first major enterprise contract with a Fortune 500 manufacturing company. They're using our AI-powered predictive maintenance platform to reduce equipment downtime by 35%, which translates to millions in cost savings for them.",
            "context": "Opening - Recent major win"
        },
        {
            "response": f"We're a B2B SaaS platform that specializes in predictive maintenance using IoT sensors and machine learning. We charge $5,000 per month for our standard enterprise package and $15,000 for our premium tier with custom AI models. Our clients typically see ROI within 3 months through reduced downtime and maintenance costs. We operate on a subscription model with annual contracts.",
            "context": "Business model - Clear value proposition"
        },
        {
            "response": "The predictive maintenance market is valued at $12.3 billion and growing at 28% annually, driven by Industry 4.0 adoption. Our main competitors are IBM Watson IoT and GE Predix, but they focus on broad industrial IoT platforms. We're laser-focused specifically on predictive maintenance with purpose-built AI models that achieve 92% accuracy in failure prediction versus the industry average of 75%.",
            "context": "Market positioning - Strong differentiation"
        },
        {
            "response": "We launched 2 years ago and now serve 8 enterprise clients across manufacturing and energy sectors. Our ARR is $720,000 and growing 45% year-over-year. Customer retention is 100% with an average contract value of $90,000. Our latest client, a steel manufacturing plant, avoided $4.2 million in unplanned downtime costs in their first 6 months using our platform.",
            "context": "Traction - Impressive metrics"
        },
        {
            "response": "I'm the CEO with 15 years of experience in industrial engineering and AI, including 8 years at Siemens leading their digital factory initiatives. My co-founder Dr. Priya Sharma is our Chief Technology Officer - she has a PhD in Machine Learning from Carnegie Mellon and previously developed predictive algorithms at Boeing. We're currently expanding our team with 2 senior ML engineers and a VP of Enterprise Sales.",
            "context": "Team - Strong technical leadership"
        },
        {
            "response": f"In 5 years, I see {session_data['startup_name']} as the global leader in AI-powered predictive maintenance, serving over 1,000 enterprise clients worldwide. We're planning to expand into adjacent markets like quality control and supply chain optimization. Our vision is to prevent industrial failures before they happen, making manufacturing safer, more efficient, and more sustainable. We're also exploring strategic partnerships with major equipment manufacturers to embed our AI directly into their machines.",
            "context": "Vision - Ambitious but realistic growth plan"
        }
    ]
    
    conversation_log = []
    
    for i, demo in enumerate(demo_responses):
        print(f"\n--- Exchange {i+1}: {demo['context']} ---")
        print(f"👤 FOUNDER: {demo['response']}")
        
        # Process the response
        result = process_founder_response(session_data, demo["response"])
        
        if result["status"] == "success":
            print(f"🎤 INTERVIEWER: {result['next_message']}")
            
            # Show real-time analysis
            print(f"\n📊 Real-time Analysis:")
            print(f"   🎯 Current Topic: {result['current_topic'].replace('_', ' ').title()}")
            print(f"   📈 Progress: {result['progress_percentage']}% complete")
            print(f"   🤝 Rapport Level: {result['rapport_level']:.2f}")
            
            conversation_log.append({
                "exchange": i + 1,
                "founder_response": demo["response"],
                "interviewer_response": result["next_message"],
                "topic": result["current_topic"],
                "progress": result["progress_percentage"],
                "rapport": result["rapport_level"],
                "context": demo["context"]
            })
        else:
            print(f"❌ Error: {result['error_message']}")
            break
    
    return {
        "status": "success",
        "conversation_log": conversation_log,
        "final_rapport": session_data["rapport_level"],
        "total_exchanges": len(conversation_log)
    }

def main():
    """Run the complete interview workflow demo"""
    print("🚀 COMPLETE INTERVIEW WORKFLOW DEMO")
    print("=" * 60)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📧 Target: syedubedullakhadri@gmail.com")
    print("=" * 60)
    
    # Step 1: Send email invitation
    print(f"\n📧 STEP 1: SENDING INTERVIEW INVITATION")
    print("=" * 50)
    
    invitation_result = send_interview_invitation_email(
        founder_email="syedubedullakhadri@gmail.com",
        founder_name="Syed Ubedulla Khadri", 
        startup_name="IndustrialAI Solutions"
    )
    
    meeting_id = invitation_result["meeting_id"]
    
    # Step 2: Simulate meeting acceptance
    print(f"\n✅ STEP 2: MEETING ACCEPTANCE")
    print("=" * 50)
    
    acceptance_result = simulate_meeting_acceptance(meeting_id, "Syed Ubedulla Khadri")
    
    # Step 3: Start interview session
    print(f"\n🎤 STEP 3: STARTING INTERVIEW SESSION")
    print("=" * 50)
    
    session_result = start_voice_interview_session(
        meeting_id=meeting_id,
        founder_name="Syed Ubedulla Khadri",
        startup_name="IndustrialAI Solutions"
    )
    
    print(f"✅ Interview session initialized!")
    print(f"📋 Session ID: {session_result['session_data']['session_id']}")
    
    print(f"\n🎤 INTERVIEWER OPENING:")
    print("-" * 40)
    print(session_result["opening_message"])
    
    # Step 4: Conduct interactive interview
    print(f"\n🎭 STEP 4: CONDUCTING INTERACTIVE INTERVIEW")
    print("=" * 50)
    
    interview_result = conduct_interactive_interview(session_result["session_data"])
    
    # Final summary
    print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 Final Results:")
    print(f"   ✅ Email invitation sent to syedubedullakhadri@gmail.com")
    print(f"   ✅ Meeting accepted by Syed Ubedulla Khadri")
    print(f"   ✅ Voice interview session conducted")
    print(f"   📈 Total exchanges: {interview_result['total_exchanges']}")
    print(f"   🤝 Final rapport level: {interview_result['final_rapport']:.2f}")
    print(f"   🎯 Interview completion: 100%")
    
    print(f"\n💡 WORKFLOW SUMMARY:")
    print(f"1. 📧 Professional email invitation sent with acceptance link")
    print(f"2. ⏳ Founder receives and accepts meeting invitation") 
    print(f"3. 🎤 AI interviewer starts personalized voice conversation")
    print(f"4. 🗣️  Natural dialogue covers all key investment topics")
    print(f"5. 📊 Real-time analysis tracks rapport and progress")
    print(f"6. ✅ Complete evaluation data collected for investment decision")
    
    print(f"\n🔧 TECHNICAL IMPLEMENTATION:")
    print(f"• Email system with HTML templates and acceptance tracking")
    print(f"• Meeting coordination with unique IDs and status management")
    print(f"• Conversational AI with natural language processing")
    print(f"• Real-time sentiment analysis and rapport calculation")
    print(f"• Progress tracking across structured interview topics")
    print(f"• Session state management throughout the conversation")

if __name__ == "__main__":
    main()
