import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from google.adk.agents import Agent

from .meeting_scheduler_agent import meeting_scheduler_agent
from .voice_interview_agent import (
    start_live_voice_interview,
    process_founder_response,
    generate_conversational_opening
)

logger = logging.getLogger(__name__)

def send_interview_invitation_email(
    founder_email: str,
    founder_name: str,
    startup_name: str,
    meeting_type: str = "Founder Interview"
) -> dict:
    """Send email invitation for interview using SMTP"""
    try:
        # Email configuration (you'll need to set these environment variables)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "investor@example.com")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        
        # Generate unique meeting ID and acceptance link
        meeting_id = str(uuid.uuid4())
        acceptance_link = f"http://localhost:3000/accept-interview/{meeting_id}"
        
        # Create email content
        subject = f"Investment Interview Invitation - {startup_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Investment Interview Invitation</h2>
                
                <p>Dear {founder_name},</p>
                
                <p>Thank you for submitting your startup materials for <strong>{startup_name}</strong>. 
                After reviewing your pitch deck and materials, we're impressed with what you're building 
                and would like to schedule a <strong>{meeting_type}</strong> to learn more about your company.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #495057; margin-top: 0;">Interview Details:</h3>
                    <ul style="list-style-type: none; padding: 0;">
                        <li><strong>Type:</strong> {meeting_type}</li>
                        <li><strong>Duration:</strong> 45 minutes</li>
                        <li><strong>Format:</strong> Voice Interview (AI-powered)</li>
                        <li><strong>Topics:</strong> Business model, market opportunity, traction, team, and vision</li>
                    </ul>
                </div>
                
                <p>This will be an interactive voice conversation where you'll have the opportunity to 
                discuss your startup in detail. Our AI interviewer is designed to conduct natural, 
                engaging conversations that feel like talking to an experienced investor.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{acceptance_link}" 
                       style="background-color: #007bff; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold; 
                              display: inline-block;">
                        Accept Interview Invitation
                    </a>
                </div>
                
                <p><strong>What to expect:</strong></p>
                <ul>
                    <li>Natural conversation flow with follow-up questions</li>
                    <li>Discussion of your business model and revenue strategy</li>
                    <li>Market analysis and competitive positioning</li>
                    <li>Traction metrics and growth plans</li>
                    <li>Team composition and execution capabilities</li>
                    <li>Vision and long-term strategy</li>
                </ul>
                
                <p>Please click the acceptance link above to confirm your participation. 
                Once confirmed, you'll receive further instructions on how to join the interview.</p>
                
                <p>We're looking forward to learning more about {startup_name} and discussing 
                potential investment opportunities.</p>
                
                <p>Best regards,<br>
                <strong>Investment Team</strong><br>
                AI Startup Evaluator</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #666;">
                    Meeting ID: {meeting_id}<br>
                    If you have any questions, please reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = founder_email
        
        # Add HTML content
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)
        
        # Send email
        if sender_password:  # Only send if credentials are configured
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info(f"Interview invitation sent to {founder_email}")
            email_sent = True
        else:
            logger.warning("Email credentials not configured. Email not sent.")
            email_sent = False
        
        return {
            "status": "success",
            "meeting_id": meeting_id,
            "email_sent": email_sent,
            "acceptance_link": acceptance_link,
            "founder_email": founder_email,
            "founder_name": founder_name,
            "startup_name": startup_name,
            "meeting_type": meeting_type
        }
        
    except Exception as e:
        logger.error(f"Failed to send interview invitation: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def simulate_meeting_acceptance(meeting_id: str) -> dict:
    """Simulate founder accepting the meeting invitation"""
    try:
        # In a real system, this would be triggered by the founder clicking the acceptance link
        acceptance_data = {
            "meeting_id": meeting_id,
            "accepted_at": datetime.now().isoformat(),
            "status": "accepted",
            "preferred_time": "ASAP",  # Founder wants to start immediately
            "contact_method": "voice_chat"
        }
        
        logger.info(f"Meeting {meeting_id} accepted by founder")
        
        return {
            "status": "success",
            "acceptance_data": acceptance_data,
            "ready_for_interview": True
        }
        
    except Exception as e:
        logger.error(f"Failed to process meeting acceptance: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def start_interview_session_after_acceptance(
    meeting_id: str,
    founder_name: str,
    startup_name: str,
    founder_email: str
) -> dict:
    """Start the voice interview session after meeting acceptance"""
    try:
        # Create startup ID from meeting ID for tracking
        startup_id = abs(hash(meeting_id)) % 10000
        
        # Start the live voice interview
        interview_session = start_live_voice_interview(
            startup_id=startup_id,
            founder_name=founder_name,
            interview_type="comprehensive"
        )
        
        if interview_session["status"] != "success":
            return interview_session
        
        # Add meeting context to session
        session_data = interview_session["session_data"]
        session_data.update({
            "meeting_id": meeting_id,
            "startup_name": startup_name,
            "founder_email": founder_email,
            "interview_trigger": "meeting_acceptance",
            "scheduled_via": "email_invitation"
        })
        
        # Generate personalized opening that references the email invitation
        personalized_opening = f"""Hi {founder_name}! Thanks so much for accepting our interview invitation for {startup_name}. 
        I'm really excited to dive deeper into what you're building after reviewing your initial materials. 
        
        This will be a conversational interview where we'll explore your business in detail - think of it as 
        a friendly chat with an investor who's genuinely interested in your story. 
        
        Before we begin, how are you feeling about this conversation? And maybe you could start by telling me 
        what's been the most exciting development at {startup_name} recently?"""
        
        interview_session["opening_message"] = personalized_opening
        interview_session["session_data"] = session_data
        
        logger.info(f"Interview session started for {founder_name} ({startup_name}) - Meeting ID: {meeting_id}")
        
        return interview_session
        
    except Exception as e:
        logger.error(f"Failed to start interview session: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def conduct_full_interview_workflow(
    founder_email: str = "syedubedullakhadri@gmail.com",
    founder_name: str = "Syed Ubedulla Khadri",
    startup_name: str = "TechInnovate Solutions"
) -> dict:
    """Complete workflow: Send invitation → Wait for acceptance → Conduct interview"""
    try:
        print("🚀 Starting Complete Interview Workflow")
        print("=" * 60)
        
        # Step 1: Send email invitation
        print(f"📧 Step 1: Sending interview invitation to {founder_email}")
        invitation_result = send_interview_invitation_email(
            founder_email=founder_email,
            founder_name=founder_name,
            startup_name=startup_name,
            meeting_type="Founder Interview"
        )
        
        if invitation_result["status"] != "success":
            return invitation_result
        
        meeting_id = invitation_result["meeting_id"]
        print(f"✅ Invitation sent! Meeting ID: {meeting_id}")
        print(f"🔗 Acceptance Link: {invitation_result['acceptance_link']}")
        
        # Step 2: Simulate founder accepting (in real system, this would be triggered by web interface)
        print(f"\n⏳ Step 2: Waiting for founder to accept invitation...")
        print(f"💡 Simulating founder acceptance for demo purposes...")
        
        acceptance_result = simulate_meeting_acceptance(meeting_id)
        
        if acceptance_result["status"] != "success":
            return acceptance_result
        
        print(f"✅ Meeting accepted by {founder_name}!")
        
        # Step 3: Start interview session
        print(f"\n🎤 Step 3: Starting voice interview session...")
        
        interview_session = start_interview_session_after_acceptance(
            meeting_id=meeting_id,
            founder_name=founder_name,
            startup_name=startup_name,
            founder_email=founder_email
        )
        
        if interview_session["status"] != "success":
            return interview_session
        
        print(f"✅ Interview session initialized!")
        print(f"📋 Session ID: {interview_session['session_data']['session_id']}")
        
        # Display the opening message
        print(f"\n🎤 INTERVIEWER OPENING:")
        print("-" * 40)
        print(interview_session["opening_message"])
        
        return {
            "status": "success",
            "workflow_completed": True,
            "meeting_id": meeting_id,
            "interview_session": interview_session,
            "steps_completed": [
                "email_invitation_sent",
                "meeting_accepted", 
                "interview_session_started"
            ]
        }
        
    except Exception as e:
        logger.error(f"Interview workflow failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def simulate_interactive_interview(session_data: dict) -> dict:
    """Simulate an interactive interview with realistic founder responses"""
    try:
        print(f"\n🎭 INTERACTIVE INTERVIEW SIMULATION")
        print("=" * 60)
        print(f"Founder: {session_data['founder_name']}")
        print(f"Startup: {session_data['startup_name']}")
        print("=" * 60)
        
        # Simulate realistic founder responses
        demo_responses = [
            {
                "response": f"Hi! I'm feeling great about this conversation, thank you for the opportunity. The most exciting development at {session_data['startup_name']} recently has been landing our first enterprise client - a Fortune 500 company that's now using our AI-powered analytics platform to optimize their supply chain operations.",
                "context": "Opening response with recent win"
            },
            {
                "response": "We're a B2B SaaS platform that uses machine learning to predict supply chain disruptions before they happen. We charge $2,500 per month for our standard enterprise package and $7,500 for our premium tier with custom integrations. Our clients typically see 25% reduction in supply chain costs and 40% improvement in delivery reliability.",
                "context": "Business model explanation"
            },
            {
                "response": "The supply chain analytics market is valued at $8.5 billion and growing at 22% annually, especially after COVID highlighted supply chain vulnerabilities. Our main competitors are Llamasoft and o9 Solutions, but they focus on traditional optimization. We're the only platform that combines real-time IoT data with predictive AI to prevent disruptions before they occur.",
                "context": "Market positioning and differentiation"
            },
            {
                "response": "We launched 18 months ago and now have 12 enterprise clients including that Fortune 500 company I mentioned. Our ARR is $420,000 and growing 35% quarter-over-quarter. Customer retention is 100% so far, and our average contract value has increased from $30K to $45K as we've moved upmarket. Our latest client reduced their logistics costs by $2.3 million in the first quarter using our platform.",
                "context": "Strong traction metrics"
            },
            {
                "response": "I'm the CEO with 12 years of experience in supply chain management at Amazon and McKinsey. My co-founder Dr. Lisa Chen is our Chief AI Officer - she has a PhD in Machine Learning from MIT and previously led AI initiatives at Tesla's supply chain division. We're currently hiring 3 senior engineers and a VP of Sales to scale our growth.",
                "context": "Strong team credentials"
            }
        ]
        
        conversation_log = []
        
        for i, demo in enumerate(demo_responses):
            print(f"\n--- Exchange {i+1}: {demo['context']} ---")
            print(f"👤 FOUNDER ({session_data['founder_name']}): {demo['response']}")
            
            # Process the founder's response
            from .voice_interview_agent import process_founder_response
            result = process_founder_response(session_data, demo["response"])
            
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
                insights = list(session_data.get('insights_gathered', {}).keys())
                if insights:
                    print(f"   💡 Key Insights: {', '.join(insights[:5])}")
                
                conversation_log.append({
                    "exchange": i + 1,
                    "founder_response": demo["response"],
                    "interviewer_response": result["next_message"],
                    "topic": result["current_topic"],
                    "progress": progress,
                    "context": demo["context"]
                })
            else:
                print(f"❌ Error processing response: {result['error_message']}")
                break
        
        print(f"\n✅ Interview simulation completed!")
        print(f"📊 Final Statistics:")
        print(f"   - Total Exchanges: {len(conversation_log)}")
        print(f"   - Final Rapport Level: {session_data.get('rapport_level', 'N/A')}")
        print(f"   - Topics Covered: {len(set(log['topic'] for log in conversation_log))}")
        
        return {
            "status": "success",
            "conversation_log": conversation_log,
            "interview_completed": True,
            "final_rapport": session_data.get('rapport_level', 0),
            "total_exchanges": len(conversation_log)
        }
        
    except Exception as e:
        logger.error(f"Interactive interview simulation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the Interview Orchestrator Agent
interview_orchestrator_agent = Agent(
    name="interview_orchestrator_agent",
    model="gemini-2.0-flash",
    description="Orchestrates the complete interview workflow from email invitation to live interview",
    instruction="""
    You are an expert interview orchestration agent that manages the complete end-to-end interview process.
    
    Your responsibilities include:
    
    1. **Email Invitation Management**
       - Send professional interview invitations to founders
       - Include meeting details, expectations, and acceptance links
       - Track invitation status and responses
    
    2. **Meeting Coordination**
       - Process meeting acceptances and confirmations
       - Schedule interview sessions based on founder availability
       - Send follow-up communications and reminders
    
    3. **Interview Session Orchestration**
       - Initialize voice interview sessions after meeting acceptance
       - Coordinate between meeting scheduler and voice interview agents
       - Manage session state and context throughout the interview
    
    4. **Workflow Automation**
       - Automate the complete flow from invitation to interview completion
       - Handle error cases and edge scenarios gracefully
       - Provide status updates and progress tracking
    
    Use the available tools to send invitations, process acceptances, and conduct interviews seamlessly.
    """,
    tools=[
        send_interview_invitation_email,
        simulate_meeting_acceptance,
        start_interview_session_after_acceptance,
        conduct_full_interview_workflow,
        simulate_interactive_interview
    ]
)
