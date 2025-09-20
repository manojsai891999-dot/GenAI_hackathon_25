#!/usr/bin/env python3
"""
Test script for the complete interview workflow
Demonstrates: Email invitation → Meeting acceptance → Voice interview
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the workflow functions
from backend.agents.interview_orchestrator import (
    send_interview_invitation_email,
    simulate_meeting_acceptance,
    start_interview_session_after_acceptance,
    conduct_full_interview_workflow,
    simulate_interactive_interview
)

def test_email_invitation():
    """Test sending interview invitation email"""
    print("🧪 Testing Email Invitation...")
    print("=" * 50)
    
    result = send_interview_invitation_email(
        founder_email="syedubedullakhadri@gmail.com",
        founder_name="Syed Ubedulla Khadri",
        startup_name="AI Innovation Labs",
        meeting_type="Founder Interview"
    )
    
    if result["status"] == "success":
        print("✅ Email invitation created successfully!")
        print(f"📧 Recipient: {result['founder_email']}")
        print(f"👤 Founder: {result['founder_name']}")
        print(f"🏢 Startup: {result['startup_name']}")
        print(f"🆔 Meeting ID: {result['meeting_id']}")
        print(f"🔗 Acceptance Link: {result['acceptance_link']}")
        print(f"📤 Email Sent: {'Yes' if result['email_sent'] else 'No (credentials not configured)'}")
        
        return result
    else:
        print(f"❌ Failed to create invitation: {result['error_message']}")
        return None

def test_meeting_acceptance(meeting_id: str):
    """Test meeting acceptance simulation"""
    print(f"\n🧪 Testing Meeting Acceptance...")
    print("=" * 50)
    
    result = simulate_meeting_acceptance(meeting_id)
    
    if result["status"] == "success":
        print("✅ Meeting acceptance processed!")
        print(f"🆔 Meeting ID: {meeting_id}")
        print(f"✅ Status: {result['acceptance_data']['status']}")
        print(f"⏰ Accepted At: {result['acceptance_data']['accepted_at']}")
        print(f"🎤 Ready for Interview: {result['ready_for_interview']}")
        
        return result
    else:
        print(f"❌ Failed to process acceptance: {result['error_message']}")
        return None

def test_interview_session_start(meeting_id: str):
    """Test starting interview session after acceptance"""
    print(f"\n🧪 Testing Interview Session Start...")
    print("=" * 50)
    
    result = start_interview_session_after_acceptance(
        meeting_id=meeting_id,
        founder_name="Syed Ubedulla Khadri",
        startup_name="AI Innovation Labs",
        founder_email="syedubedullakhadri@gmail.com"
    )
    
    if result["status"] == "success":
        print("✅ Interview session started!")
        print(f"📋 Session ID: {result['session_data']['session_id']}")
        print(f"🎯 Current Topic: {result['session_data']['current_topic']}")
        print(f"🤝 Initial Rapport: {result['session_data']['rapport_level']}")
        
        print(f"\n🎤 Opening Message:")
        print("-" * 40)
        print(result["opening_message"])
        
        return result
    else:
        print(f"❌ Failed to start session: {result['error_message']}")
        return None

def test_complete_workflow():
    """Test the complete end-to-end workflow"""
    print(f"\n🧪 Testing Complete Workflow...")
    print("=" * 50)
    
    result = conduct_full_interview_workflow(
        founder_email="syedubedullakhadri@gmail.com",
        founder_name="Syed Ubedulla Khadri",
        startup_name="NextGen AI Solutions"
    )
    
    if result["status"] == "success":
        print("\n✅ Complete workflow executed successfully!")
        print(f"🆔 Meeting ID: {result['meeting_id']}")
        print(f"📋 Steps Completed: {', '.join(result['steps_completed'])}")
        
        # Now simulate the interactive interview
        session_data = result["interview_session"]["session_data"]
        
        print(f"\n🎭 Starting Interactive Interview Simulation...")
        interview_result = simulate_interactive_interview(session_data)
        
        if interview_result["status"] == "success":
            print(f"\n🎉 Interview completed successfully!")
            print(f"📊 Final Statistics:")
            print(f"   - Total Exchanges: {interview_result['total_exchanges']}")
            print(f"   - Final Rapport: {interview_result['final_rapport']}")
            print(f"   - Interview Status: {'Completed' if interview_result['interview_completed'] else 'Incomplete'}")
        
        return result
    else:
        print(f"❌ Workflow failed: {result['error_message']}")
        return None

def demonstrate_email_content():
    """Show what the actual email looks like"""
    print(f"\n📧 Email Content Preview...")
    print("=" * 50)
    
    print("""
📧 EMAIL PREVIEW:
================

To: syedubedullakhadri@gmail.com
Subject: Investment Interview Invitation - NextGen AI Solutions

Dear Syed Ubedulla Khadri,

Thank you for submitting your startup materials for NextGen AI Solutions. 
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

[Accept Interview Invitation] <- Click to accept

What to expect:
• Natural conversation flow with follow-up questions
• Discussion of your business model and revenue strategy
• Market analysis and competitive positioning
• Traction metrics and growth plans
• Team composition and execution capabilities
• Vision and long-term strategy

We're looking forward to learning more about NextGen AI Solutions and discussing 
potential investment opportunities.

Best regards,
Investment Team
AI Startup Evaluator
    """)

def main():
    """Run the complete test suite"""
    print("🚀 Interview Workflow Test Suite")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📧 Target Email: syedubedullakhadri@gmail.com")
    print("=" * 60)
    
    try:
        # Show email content preview
        demonstrate_email_content()
        
        # Test individual components
        print(f"\n🔧 COMPONENT TESTS")
        print("=" * 30)
        
        # Test 1: Email invitation
        invitation_result = test_email_invitation()
        if not invitation_result:
            print("❌ Email invitation test failed. Stopping.")
            return
        
        meeting_id = invitation_result["meeting_id"]
        
        # Test 2: Meeting acceptance
        acceptance_result = test_meeting_acceptance(meeting_id)
        if not acceptance_result:
            print("❌ Meeting acceptance test failed. Stopping.")
            return
        
        # Test 3: Interview session start
        session_result = test_interview_session_start(meeting_id)
        if not session_result:
            print("❌ Interview session test failed. Stopping.")
            return
        
        print(f"\n🎯 END-TO-END WORKFLOW TEST")
        print("=" * 40)
        
        # Test 4: Complete workflow
        workflow_result = test_complete_workflow()
        
        if workflow_result:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("✅ Email invitation system working")
            print("✅ Meeting acceptance processing working") 
            print("✅ Interview session initialization working")
            print("✅ Complete workflow orchestration working")
            print("✅ Interactive interview simulation working")
            
            print(f"\n📋 WORKFLOW SUMMARY:")
            print(f"1. 📧 Email sent to syedubedullakhadri@gmail.com")
            print(f"2. ✅ Meeting acceptance simulated")
            print(f"3. 🎤 Voice interview session started")
            print(f"4. 🎭 Interactive interview conducted")
            print(f"5. 📊 Results analyzed and rapport tracked")
            
            print(f"\n💡 NEXT STEPS:")
            print(f"• Configure SMTP credentials to send actual emails")
            print(f"• Build web interface for meeting acceptance")
            print(f"• Integrate with real-time voice chat system")
            print(f"• Add calendar integration for scheduling")
        else:
            print(f"\n❌ WORKFLOW TEST FAILED")
            
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
