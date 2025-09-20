#!/usr/bin/env python3
"""
Live Voice Interview System
Conducts real-time voice interviews with startup founders
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
import speech_recognition as sr
import pyttsx3
from queue import Queue

class LiveVoiceInterviewer:
    """Real-time voice interview system"""
    
    def __init__(self, founder_name="Syed Ubedulla Khadri", startup_name="Your Startup"):
        self.founder_name = founder_name
        self.startup_name = startup_name
        
        # Initialize speech recognition and text-to-speech
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS voice
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to use a professional-sounding voice
            for voice in voices:
                if 'english' in voice.name.lower() and ('female' in voice.name.lower() or 'male' in voice.name.lower()):
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        self.tts_engine.setProperty('rate', 160)  # Slightly slower for clarity
        self.tts_engine.setProperty('volume', 0.9)
        
        # Interview state
        self.session_data = {
            "session_id": f"live_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "founder_name": founder_name,
            "startup_name": startup_name,
            "start_time": datetime.now().isoformat(),
            "current_topic": "introduction",
            "conversation_history": [],
            "insights_gathered": {},
            "rapport_level": 0.5,
            "interview_active": True
        }
        
        # Audio processing queue
        self.audio_queue = Queue()
        self.listening = False
        
        print("🎤 Initializing voice interview system...")
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            print("🔧 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibrated successfully!")
        except Exception as e:
            print(f"⚠️  Microphone calibration warning: {str(e)}")
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"🎤 INTERVIEWER: {text}")
        print("🔊 Speaking...")
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {str(e)}")
            print("💡 Please read the interviewer's message above")
        
        print("✅ Finished speaking. Your turn to respond!")
    
    def listen_for_response(self, timeout=30):
        """Listen for founder's voice response"""
        print(f"\n👂 Listening for your response... (Speak now, {timeout}s timeout)")
        print("🎙️  Say 'stop interview' to end the session")
        
        try:
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=60)
            
            print("🔄 Processing your response...")
            
            # Convert speech to text
            try:
                response_text = self.recognizer.recognize_google(audio)
                print(f"👤 FOUNDER ({self.founder_name}): {response_text}")
                
                # Check for stop command
                if "stop interview" in response_text.lower():
                    return "STOP_INTERVIEW"
                
                return response_text
                
            except sr.UnknownValueError:
                print("❌ Sorry, I couldn't understand what you said. Could you please repeat?")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {str(e)}")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ No response detected within timeout period.")
            return None
        except Exception as e:
            print(f"❌ Audio error: {str(e)}")
            return None
    
    def analyze_response(self, response_text):
        """Analyze founder's response for insights and sentiment"""
        if not response_text:
            return {"quality_score": 0, "sentiment_score": 0.5, "insights": {}}
        
        word_count = len(response_text.split())
        
        # Sentiment analysis
        positive_words = ["excited", "fantastic", "great", "amazing", "successful", "growing", "confident", "passionate"]
        negative_words = ["challenging", "difficult", "struggling", "worried", "concerned", "problem"]
        
        positive_count = sum(1 for word in positive_words if word.lower() in response_text.lower())
        negative_count = sum(1 for word in negative_words if word.lower() in response_text.lower())
        
        sentiment_score = 0.5  # neutral
        if positive_count + negative_count > 0:
            sentiment_score = positive_count / (positive_count + negative_count)
        
        # Extract business insights
        insights = {}
        business_keywords = {
            "revenue": ["revenue", "money", "income", "sales", "profit"],
            "customers": ["customers", "clients", "users", "market"],
            "team": ["team", "founder", "employees", "hiring"],
            "funding": ["funding", "investment", "capital", "raise"],
            "growth": ["growth", "growing", "scale", "expansion"]
        }
        
        for category, keywords in business_keywords.items():
            if any(keyword in response_text.lower() for keyword in keywords):
                insights[category] = True
        
        quality_score = min(word_count / 50, 1.0) * 0.6 + sentiment_score * 0.4
        
        return {
            "quality_score": quality_score,
            "sentiment_score": sentiment_score,
            "insights": insights,
            "word_count": word_count
        }
    
    def generate_next_question(self, response_analysis):
        """Generate the next interview question based on current context"""
        current_topic = self.session_data["current_topic"]
        founder_name = self.founder_name
        startup_name = self.startup_name
        
        # Update rapport based on response quality
        if response_analysis["quality_score"] > 0.7:
            self.session_data["rapport_level"] = min(self.session_data["rapport_level"] + 0.1, 1.0)
        
        # Topic-based questions with natural transitions
        topic_questions = {
            "introduction": {
                "next_topic": "business_model",
                "question": f"That's wonderful to hear, {founder_name}! I'm really excited to learn more about {startup_name}. Let's dive into the business side - how exactly do you make money? What's your revenue model?"
            },
            "business_model": {
                "next_topic": "market_opportunity", 
                "question": f"That's a solid business model! Now I'm curious about the market you're targeting. How big is this opportunity, and who are your main competitors?"
            },
            "market_opportunity": {
                "next_topic": "traction_metrics",
                "question": f"The market sounds promising! Let's talk about your traction. What does your growth look like? Can you share some key metrics or customer success stories?"
            },
            "traction_metrics": {
                "next_topic": "team_execution",
                "question": f"Those are encouraging numbers! Tell me about the team behind this success. What's your background, and how are you thinking about scaling the team?"
            },
            "team_execution": {
                "next_topic": "funding_vision",
                "question": f"Sounds like you have a strong foundation! Looking ahead, what are your funding needs and long-term vision for {startup_name}?"
            },
            "funding_vision": {
                "next_topic": "conclusion",
                "question": f"That's an exciting vision, {founder_name}! Before we wrap up, what questions do you have for me about our investment process or what we look for in startups?"
            }
        }
        
        if current_topic in topic_questions:
            transition = topic_questions[current_topic]
            self.session_data["current_topic"] = transition["next_topic"]
            return transition["question"]
        else:
            return f"Thank you so much for this conversation, {founder_name}! This has been really insightful. We'll be in touch soon with next steps."
    
    def conduct_live_interview(self):
        """Conduct the complete live voice interview"""
        print("\n🚀 STARTING LIVE VOICE INTERVIEW")
        print("=" * 60)
        print(f"👤 Founder: {self.founder_name}")
        print(f"🏢 Startup: {self.startup_name}")
        print(f"📋 Session: {self.session_data['session_id']}")
        print("=" * 60)
        
        # Opening message
        opening_message = f"""Hi {self.founder_name}! Welcome to your live voice interview. 
        I'm really excited to learn about {self.startup_name} and what you're building. 
        
        This will be a natural conversation where we'll explore your business, market, traction, and vision. 
        Just speak naturally - I'll ask follow-up questions based on your responses.
        
        To get started, could you tell me a bit about yourself and what inspired you to start {self.startup_name}? 
        What problem are you solving?"""
        
        self.speak(opening_message)
        
        # Main interview loop
        exchange_count = 0
        max_exchanges = 6  # Limit to prevent overly long interviews
        
        while self.session_data["interview_active"] and exchange_count < max_exchanges:
            exchange_count += 1
            print(f"\n--- Exchange {exchange_count} ---")
            
            # Listen for founder's response
            response = self.listen_for_response(timeout=45)
            
            if response == "STOP_INTERVIEW":
                self.speak(f"Thank you for the interview, {self.founder_name}! It was great talking with you.")
                break
            elif response is None:
                self.speak("I didn't catch that. Let me ask you a different question.")
                continue
            
            # Analyze the response
            analysis = self.analyze_response(response)
            
            # Update conversation history
            self.session_data["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "founder",
                "content": response,
                "analysis": analysis
            })
            
            # Update insights
            self.session_data["insights_gathered"].update(analysis["insights"])
            
            # Generate next question
            next_question = self.generate_next_question(analysis)
            
            # Add interviewer response to history
            self.session_data["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "interviewer",
                "content": next_question,
                "topic": self.session_data["current_topic"]
            })
            
            # Show real-time analysis
            print(f"\n📊 Real-time Analysis:")
            print(f"   🎯 Current Topic: {self.session_data['current_topic'].replace('_', ' ').title()}")
            print(f"   🤝 Rapport Level: {self.session_data['rapport_level']:.2f}")
            print(f"   💡 Insights: {', '.join(self.session_data['insights_gathered'].keys())}")
            
            # Check if we've reached conclusion
            if self.session_data["current_topic"] == "conclusion":
                self.speak(next_question)
                
                # Final response
                final_response = self.listen_for_response(timeout=30)
                if final_response:
                    self.speak(f"Perfect! Thank you so much for your time, {self.founder_name}. This has been a fantastic conversation about {self.startup_name}. We'll review everything and get back to you with next steps within 48 hours. Have a great day!")
                break
            else:
                # Continue with next question
                self.speak(next_question)
        
        # Interview summary
        self.print_interview_summary()
    
    def print_interview_summary(self):
        """Print final interview summary"""
        print(f"\n🎉 INTERVIEW COMPLETED!")
        print("=" * 60)
        print(f"📊 Interview Summary:")
        print(f"   - Duration: {len(self.session_data['conversation_history']) // 2} exchanges")
        print(f"   - Final Rapport: {self.session_data['rapport_level']:.2f}")
        print(f"   - Topics Covered: {self.session_data['current_topic'].replace('_', ' ').title()}")
        print(f"   - Key Insights: {', '.join(self.session_data['insights_gathered'].keys())}")
        
        print(f"\n💾 Session Data:")
        print(f"   - Session ID: {self.session_data['session_id']}")
        print(f"   - Founder: {self.founder_name}")
        print(f"   - Startup: {self.startup_name}")
        
        print(f"\n✅ Interview data ready for investment evaluation!")

def main():
    """Main function to start live interview"""
    print("🎤 LIVE VOICE INTERVIEW SYSTEM")
    print("=" * 50)
    
    # Get founder details
    founder_name = input("👤 Enter founder name (or press Enter for 'Syed Ubedulla Khadri'): ").strip()
    if not founder_name:
        founder_name = "Syed Ubedulla Khadri"
    
    startup_name = input("🏢 Enter startup name (or press Enter for 'Your Startup'): ").strip()
    if not startup_name:
        startup_name = "Your Startup"
    
    print(f"\n🚀 Initializing interview for {founder_name} from {startup_name}...")
    
    try:
        # Create and start interview
        interviewer = LiveVoiceInterviewer(founder_name, startup_name)
        
        print(f"\n🎙️  MICROPHONE TEST")
        print("Please say 'test' to verify your microphone is working...")
        test_response = interviewer.listen_for_response(timeout=10)
        
        if test_response:
            print(f"✅ Microphone working! Detected: '{test_response}'")
            
            input("\n🎬 Press Enter when you're ready to start the live interview...")
            interviewer.conduct_live_interview()
        else:
            print("❌ Microphone test failed. Please check your microphone and try again.")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Interview stopped by user.")
    except Exception as e:
        print(f"\n❌ Interview error: {str(e)}")
        print("💡 Make sure you have a working microphone and speakers/headphones.")

if __name__ == "__main__":
    main()
