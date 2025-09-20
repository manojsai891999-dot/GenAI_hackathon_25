#!/usr/bin/env python3
"""
Voice Interview Agent Launcher
Starts the conversational voice interview system
"""

import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def start_voice_interview_agent():
    """Start the voice interview agent with Syed Ubedulla Khadri"""
    
    print("🎤 STARTING VOICE INTERVIEW AGENT")
    print("=" * 60)
    print(f"📅 Session Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 Founder: Syed Ubedulla Khadri")
    print(f"📧 Email: syedubedullakhadri@gmail.com")
    print("=" * 60)
    
    try:
        # Import voice interview functions
        from backend.agents.voice_interview_agent import (
            start_live_voice_interview,
            process_founder_response,
            generate_conversational_opening
        )
        
        print("✅ Voice interview agent loaded successfully!")
        
        # Initialize interview session
        print("\n🚀 INITIALIZING INTERVIEW SESSION...")
        
        session = start_live_voice_interview(
            startup_id=12345,
            founder_name="Syed Ubedulla Khadri",
            interview_type="comprehensive"
        )
        
        if session["status"] == "success":
            print("✅ Interview session initialized!")
            
            session_data = session["session_data"]
            print(f"📋 Session ID: {session_data['session_id']}")
            print(f"🎯 Interview Type: {session_data['interview_type']}")
            
            # Start the conversation
            print(f"\n🎤 VOICE INTERVIEW AGENT ACTIVE")
            print("=" * 50)
            print("🔊 INTERVIEWER SPEAKING:")
            print("-" * 30)
            print(session["opening_message"])
            
            # Interactive conversation loop
            print(f"\n🎙️  CONVERSATION MODE ACTIVE")
            print("💡 Type your responses as if speaking to the interviewer")
            print("💡 Type 'exit' to end the interview")
            
            exchange_count = 0
            max_exchanges = 8
            
            while exchange_count < max_exchanges:
                exchange_count += 1
                
                print(f"\n--- EXCHANGE {exchange_count} ---")
                print(f"👤 {session_data['founder_name']}, your response:")
                
                try:
                    founder_response = input("🎙️  > ").strip()
                    
                    if founder_response.lower() in ['exit', 'quit', 'stop', 'end']:
                        print(f"\n🎤 INTERVIEWER: Thank you so much for your time, {session_data['founder_name']}! This has been a wonderful conversation about your startup. We'll be in touch with next steps soon.")
                        break
                    
                    if not founder_response:
                        print("⚠️  Please provide a response to continue the interview.")
                        continue
                    
                    # Process the response using the voice interview agent
                    result = process_founder_response(session_data, founder_response)
                    
                    if result["status"] == "success":
                        print(f"\n🎤 INTERVIEWER:")
                        print("-" * 30)
                        print(result["next_message"])
                        
                        # Show real-time analysis
                        progress = result["conversation_progress"]
                        print(f"\n📊 REAL-TIME ANALYSIS:")
                        print(f"   🎯 Current Topic: {result['current_topic'].replace('_', ' ').title()}")
                        print(f"   📈 Progress: {progress['progress_percentage']}%")
                        print(f"   ⏱️  Elapsed: {progress['elapsed_minutes']:.1f} min")
                        print(f"   🤝 Rapport Level: {session_data['rapport_level']:.2f}")
                        
                        # Show insights
                        insights = list(session_data.get('insights_gathered', {}).keys())
                        if insights:
                            print(f"   💡 Key Insights: {', '.join(insights[:5])}")
                        
                        # Check if interview is complete
                        if progress['progress_percentage'] >= 90:
                            print(f"\n🎉 Interview nearing completion!")
                            
                    else:
                        print(f"❌ Error processing response: {result['error_message']}")
                        
                except KeyboardInterrupt:
                    print(f"\n⏹️  Interview stopped by user.")
                    break
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
                    break
            
            # Final summary
            print(f"\n🎉 INTERVIEW SESSION COMPLETED!")
            print("=" * 50)
            print(f"📊 Final Statistics:")
            print(f"   - Total Exchanges: {exchange_count}")
            print(f"   - Final Rapport: {session_data.get('rapport_level', 0):.2f}")
            print(f"   - Session ID: {session_data['session_id']}")
            print(f"   - Founder: {session_data['founder_name']}")
            
            print(f"\n✅ Voice interview agent session complete!")
            
        else:
            print(f"❌ Failed to initialize session: {session['error_message']}")
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Running simplified voice agent simulation...")
        run_simplified_voice_agent()
        
    except Exception as e:
        print(f"❌ Voice agent error: {str(e)}")
        print("💡 Running simplified voice agent simulation...")
        run_simplified_voice_agent()

def run_simplified_voice_agent():
    """Run simplified voice agent without complex imports"""
    
    print(f"\n🎤 SIMPLIFIED VOICE AGENT")
    print("=" * 40)
    
    # Simulate voice interview agent
    founder_name = "Syed Ubedulla Khadri"
    startup_name = "TechInnovate Solutions"
    
    session_id = f"voice_session_{datetime.now().strftime('%H%M%S')}"
    
    print(f"📋 Session ID: {session_id}")
    print(f"👤 Founder: {founder_name}")
    print(f"🏢 Startup: {startup_name}")
    
    # Opening message
    opening = f"""Hi {founder_name}! Thanks for joining me today. I'm really excited to learn more about {startup_name} and what you're building. 

This will be a conversational interview where we'll explore your business in detail. Just respond naturally as if we're having a friendly chat about your startup.

To get started, could you tell me a bit about yourself and what inspired you to start {startup_name}? What problem are you solving?"""
    
    print(f"\n🔊 INTERVIEWER SPEAKING:")
    print("-" * 30)
    print(opening)
    
    # Conversation topics
    topics = [
        {
            "topic": "Business Model",
            "question": f"That's fascinating! Now I'd love to understand how {startup_name} makes money. What's your revenue model and pricing strategy?"
        },
        {
            "topic": "Market Opportunity", 
            "question": "Great business model! Tell me about your market. How big is this opportunity and who are your main competitors?"
        },
        {
            "topic": "Traction & Growth",
            "question": "Interesting market positioning! What does your traction look like? Can you share some growth metrics or customer success stories?"
        },
        {
            "topic": "Team & Vision",
            "question": f"Those are solid numbers! Tell me about your team and where you see {startup_name} in the next 5 years."
        }
    ]
    
    rapport_level = 0.5
    
    print(f"\n🎙️  INTERACTIVE MODE ACTIVE")
    print("💡 Respond as if speaking to an investor")
    print("💡 Type 'exit' to end the interview")
    
    for i, topic_data in enumerate(topics, 1):
        print(f"\n--- TOPIC {i}: {topic_data['topic']} ---")
        print(f"👤 {founder_name}, your response:")
        
        try:
            response = input("🎙️  > ").strip()
            
            if response.lower() in ['exit', 'quit', 'stop']:
                break
            
            if response:
                # Simple sentiment analysis
                positive_words = ["excited", "great", "fantastic", "successful", "growing"]
                word_count = len(response.split())
                
                if any(word in response.lower() for word in positive_words) and word_count > 20:
                    rapport_level = min(rapport_level + 0.15, 1.0)
                elif word_count > 10:
                    rapport_level = min(rapport_level + 0.05, 1.0)
                
                print(f"\n🎤 INTERVIEWER:")
                print("-" * 30)
                print(topic_data['question'])
                
                print(f"\n📊 ANALYSIS:")
                print(f"   🤝 Rapport Level: {rapport_level:.2f}")
                print(f"   📝 Response Length: {word_count} words")
                print(f"   🎯 Topic: {topic_data['topic']}")
                print(f"   📈 Progress: {((i)/len(topics)*100):.0f}%")
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Interview stopped.")
            break
    
    # Closing
    print(f"\n🎤 INTERVIEWER:")
    print("-" * 30)
    print(f"Thank you so much for this conversation, {founder_name}! I'm really impressed with what you're building at {startup_name}. We'll review everything and get back to you with next steps soon.")
    
    print(f"\n🎉 VOICE AGENT SESSION COMPLETE!")
    print(f"📊 Final Rapport Level: {rapport_level:.2f}")

if __name__ == "__main__":
    start_voice_interview_agent()
