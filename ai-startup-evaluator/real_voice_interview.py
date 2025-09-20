#!/usr/bin/env python3
"""
Real Voice-to-Voice Interview System
Conducts actual voice conversations with startup founders
"""

import speech_recognition as sr
import pyttsx3
import time
import threading
from datetime import datetime
import queue

class RealVoiceInterviewer:
    """Real voice-to-voice interview system"""
    
    def __init__(self, founder_name="Syed Ubedulla Khadri", startup_name="Your Startup"):
        self.founder_name = founder_name
        self.startup_name = startup_name
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS voice (professional, clear voice)
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to find a good voice
            for voice in voices:
                if 'english' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 150)  # Slower for clarity
        self.tts_engine.setProperty('volume', 0.9)
        
        # Interview state
        self.session_data = {
            "session_id": f"voice_interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "founder_name": founder_name,
            "startup_name": startup_name,
            "start_time": datetime.now().isoformat(),
            "current_topic": "introduction",
            "conversation_history": [],
            "insights_gathered": {},
            "rapport_level": 0.5,
            "interview_active": True
        }
        
        print("🎤 Initializing real voice interview system...")
        self._calibrate_microphone()
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            print("🔧 Calibrating microphone for ambient noise...")
            print("📢 Please be quiet for 2 seconds while I calibrate...")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print("✅ Microphone calibrated successfully!")
            
        except Exception as e:
            print(f"⚠️  Microphone calibration warning: {str(e)}")
            print("💡 Continuing anyway...")
    
    def speak(self, text):
        """Convert text to speech and speak it"""
        print(f"\n🎤 INTERVIEWER SPEAKING:")
        print("=" * 50)
        print(text)
        print("=" * 50)
        print("🔊 Speaking out loud...")
        
        try:
            # Speak the text
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            print("✅ Finished speaking.")
            
        except Exception as e:
            print(f"❌ TTS Error: {str(e)}")
            print("💡 Please read the text above")
    
    def listen_for_response(self, timeout=30):
        """Listen for founder's voice response"""
        print(f"\n👂 LISTENING FOR YOUR VOICE...")
        print("=" * 40)
        print(f"🎙️  Speak now! (Timeout: {timeout} seconds)")
        print("💡 Say 'stop interview' to end")
        print("🔴 Recording...")
        
        try:
            with self.microphone as source:
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=60)
            
            print("🔄 Processing your speech...")
            
            # Convert speech to text using Google Speech Recognition
            try:
                response_text = self.recognizer.recognize_google(audio)
                
                print(f"✅ Heard you say:")
                print(f"👤 {self.founder_name}: \"{response_text}\"")
                
                # Check for stop command
                if any(phrase in response_text.lower() for phrase in ['stop interview', 'end interview', 'quit', 'stop']):
                    return "STOP_INTERVIEW"
                
                return response_text
                
            except sr.UnknownValueError:
                print("❌ Sorry, I couldn't understand what you said.")
                print("💡 Could you please repeat that more clearly?")
                return None
                
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {str(e)}")
                print("💡 Please check your internet connection")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout period.")
            print("💡 Let me ask the question again...")
            return None
            
        except Exception as e:
            print(f"❌ Audio error: {str(e)}")
            print("💡 Please check your microphone")
            return None
    
    def analyze_response(self, response_text):
        """Analyze founder's response for insights and sentiment"""
        if not response_text:
            return {"quality_score": 0, "sentiment_score": 0.5, "insights": {}}
        
        word_count = len(response_text.split())
        
        # Enhanced sentiment analysis
        positive_words = [
            "excited", "fantastic", "great", "amazing", "successful", "growing", 
            "confident", "passionate", "love", "excellent", "strong", "profitable",
            "thrilled", "outstanding", "incredible", "wonderful", "brilliant"
        ]
        
        negative_words = [
            "challenging", "difficult", "struggling", "worried", "concerned", 
            "problem", "issue", "hard", "tough", "failing", "disappointing",
            "frustrating", "stressful", "overwhelming"
        ]
        
        positive_count = sum(1 for word in positive_words if word.lower() in response_text.lower())
        negative_count = sum(1 for word in negative_words if word.lower() in response_text.lower())
        
        sentiment_score = 0.5  # neutral baseline
        if positive_count + negative_count > 0:
            sentiment_score = positive_count / (positive_count + negative_count)
        
        # Extract business insights
        insights = {}
        business_keywords = {
            "revenue": ["revenue", "money", "income", "sales", "profit", "pricing", "$", "dollars"],
            "customers": ["customers", "clients", "users", "market", "customer", "user"],
            "team": ["team", "founder", "employees", "hiring", "ceo", "cto", "staff"],
            "funding": ["funding", "investment", "capital", "raise", "investor", "round"],
            "growth": ["growth", "growing", "scale", "expansion", "traction", "increase"],
            "product": ["product", "platform", "technology", "software", "ai", "solution"],
            "competition": ["competitors", "competition", "differentiate", "advantage", "unique"],
            "market": ["market", "industry", "sector", "opportunity", "demand"]
        }
        
        for category, keywords in business_keywords.items():
            if any(keyword in response_text.lower() for keyword in keywords):
                insights[category] = True
        
        # Quality score calculation
        length_score = min(word_count / 75, 1.0)  # Optimal around 75 words for voice
        specificity_score = len(insights) / len(business_keywords)
        
        quality_score = (length_score * 0.4 + sentiment_score * 0.3 + specificity_score * 0.3)
        
        return {
            "quality_score": quality_score,
            "sentiment_score": sentiment_score,
            "insights": insights,
            "word_count": word_count
        }
    
    def generate_next_question(self, response_analysis):
        """Generate the next interview question based on response"""
        current_topic = self.session_data["current_topic"]
        founder_name = self.founder_name
        startup_name = self.startup_name
        
        # Update rapport based on response quality and sentiment
        if response_analysis["quality_score"] > 0.8:
            self.session_data["rapport_level"] = min(self.session_data["rapport_level"] + 0.2, 1.0)
        elif response_analysis["quality_score"] > 0.6:
            self.session_data["rapport_level"] = min(self.session_data["rapport_level"] + 0.1, 1.0)
        
        # Generate enthusiastic responses based on sentiment and quality
        enthusiasm_responses = [
            "That's fantastic!",
            "That sounds incredible!",
            "I love hearing that!",
            "That's really impressive!",
            "Wow, that's exciting!",
            "That's excellent!"
        ]
        
        neutral_responses = [
            "That's interesting.",
            "I see.",
            "That makes sense.",
            "Good to know.",
            "Understood."
        ]
        
        if response_analysis["sentiment_score"] > 0.7 and response_analysis["quality_score"] > 0.6:
            enthusiasm = enthusiasm_responses[len(self.session_data["conversation_history"]) % len(enthusiasm_responses)]
        else:
            enthusiasm = neutral_responses[len(self.session_data["conversation_history"]) % len(neutral_responses)]
        
        # Topic-based questions with natural flow
        topic_questions = {
            "introduction": {
                "next_topic": "business_model",
                "question": f"{enthusiasm} Thanks for sharing that background, {founder_name}. I'm really excited to learn more about {startup_name}. Now let's dive into the business side. How exactly do you make money? What's your revenue model?"
            },
            "business_model": {
                "next_topic": "market_opportunity", 
                "question": f"{enthusiasm} That business model sounds solid. Now I'm curious about the market you're targeting. How big is this opportunity? Who are your main competitors and how do you stand out from them?"
            },
            "market_opportunity": {
                "next_topic": "traction_metrics",
                "question": f"{enthusiasm} The market opportunity sounds compelling. Let's talk about your traction. What does your growth look like? Can you share some key metrics or customer success stories?"
            },
            "traction_metrics": {
                "next_topic": "team_execution",
                "question": f"{enthusiasm} Those are encouraging numbers. Tell me about the team behind this success. What's your background? Who are your co-founders? How are you thinking about scaling the team?"
            },
            "team_execution": {
                "next_topic": "funding_vision",
                "question": f"{enthusiasm} Sounds like you have a strong foundation. Looking ahead, what are your funding needs? How much are you raising and what will you use it for? What's your long-term vision for {startup_name}?"
            },
            "funding_vision": {
                "next_topic": "conclusion",
                "question": f"{enthusiasm} That's an exciting vision, {founder_name}. Before we wrap up, what questions do you have for me? What would you like to know about our investment process?"
            }
        }
        
        if current_topic in topic_questions:
            transition = topic_questions[current_topic]
            self.session_data["current_topic"] = transition["next_topic"]
            return transition["question"]
        else:
            return f"Thank you so much for this conversation, {founder_name}. This has been really insightful learning about {startup_name}. We'll review everything and be in touch with next steps within 48 hours. I'm excited about what you're building!"
    
    def conduct_voice_interview(self):
        """Conduct the complete voice-to-voice interview"""
        print("\n🚀 STARTING REAL VOICE INTERVIEW")
        print("=" * 60)
        print(f"👤 Founder: {self.founder_name}")
        print(f"🏢 Startup: {self.startup_name}")
        print(f"📋 Session: {self.session_data['session_id']}")
        print(f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Test microphone first
        print("\n🎙️  MICROPHONE TEST")
        print("Please say 'hello' to test your microphone...")
        
        test_response = self.listen_for_response(timeout=10)
        if not test_response:
            print("❌ Microphone test failed. Please check your setup.")
            return
        
        print("✅ Microphone working! Starting interview...")
        time.sleep(1)
        
        # Opening message
        opening_message = f"""Hello {self.founder_name}! Welcome to your voice interview. I'm really excited to learn about {self.startup_name} and what you're building. 

This will be a natural conversation where we'll explore your business model, market opportunity, traction, team, and vision. Just speak naturally as if we're having a friendly chat about your startup.

To get started, could you tell me a bit about yourself and what inspired you to start {self.startup_name}? What problem are you solving and why is it important?"""
        
        self.speak(opening_message)
        
        # Main interview loop
        exchange_count = 0
        max_exchanges = 6
        
        while self.session_data["interview_active"] and exchange_count < max_exchanges:
            exchange_count += 1
            
            print(f"\n🔄 EXCHANGE {exchange_count}/{max_exchanges}")
            print("=" * 40)
            
            # Listen for founder's response
            response = self.listen_for_response(timeout=45)
            
            if response == "STOP_INTERVIEW":
                closing_message = f"Thank you for the interview, {self.founder_name}! It was wonderful talking with you about {self.startup_name}."
                self.speak(closing_message)
                break
                
            elif response is None:
                retry_message = "I didn't catch that. Let me rephrase the question."
                self.speak(retry_message)
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
            
            # Show real-time analysis
            print(f"\n📊 REAL-TIME ANALYSIS:")
            print(f"   🎯 Current Topic: {self.session_data['current_topic'].replace('_', ' ').title()}")
            print(f"   🤝 Rapport Level: {self.session_data['rapport_level']:.2f}")
            print(f"   😊 Sentiment: {analysis['sentiment_score']:.2f}")
            print(f"   📝 Quality: {analysis['quality_score']:.2f}")
            print(f"   💡 Insights: {', '.join(analysis['insights'].keys()) if analysis['insights'] else 'None'}")
            
            # Generate next question
            next_question = self.generate_next_question(analysis)
            
            # Add interviewer response to history
            self.session_data["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "speaker": "interviewer",
                "content": next_question,
                "topic": self.session_data["current_topic"]
            })
            
            # Check if we've reached conclusion
            if self.session_data["current_topic"] == "conclusion":
                self.speak(next_question)
                
                # Final response
                final_response = self.listen_for_response(timeout=30)
                if final_response and final_response != "STOP_INTERVIEW":
                    closing_message = f"""Perfect! Thank you so much for your time, {self.founder_name}. This has been a fantastic conversation about {self.startup_name}. I'm really impressed with your vision and what you're building. We'll review everything from our conversation today and get back to you with next steps within 48 hours. Based on what I've heard, I'm excited to continue the conversation with our investment team. Have a great day!"""
                    
                    self.speak(closing_message)
                break
            else:
                # Continue with next question
                self.speak(next_question)
        
        # Interview summary
        self.print_interview_summary()
    
    def print_interview_summary(self):
        """Print final interview summary"""
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.session_data['start_time'])
        duration = end_time - start_time
        
        print(f"\n🎉 VOICE INTERVIEW COMPLETED!")
        print("=" * 60)
        print(f"📊 INTERVIEW SUMMARY:")
        print(f"   ⏱️  Duration: {duration.seconds // 60} minutes, {duration.seconds % 60} seconds")
        print(f"   💬 Total Exchanges: {len(self.session_data['conversation_history']) // 2}")
        print(f"   🤝 Final Rapport Level: {self.session_data['rapport_level']:.2f}")
        print(f"   🎯 Final Topic: {self.session_data['current_topic'].replace('_', ' ').title()}")
        print(f"   💡 Business Areas Covered: {', '.join(self.session_data['insights_gathered'].keys())}")
        
        # Investment recommendation
        if self.session_data['rapport_level'] > 0.8 and len(self.session_data['insights_gathered']) >= 5:
            recommendation = "🟢 High Interest - Recommend Next Steps"
        elif self.session_data['rapport_level'] > 0.6 and len(self.session_data['insights_gathered']) >= 3:
            recommendation = "🟡 Moderate Interest - Further Evaluation"
        else:
            recommendation = "🔴 Limited Interest - Pass"
        
        print(f"\n🎯 PRELIMINARY ASSESSMENT: {recommendation}")
        print(f"✅ Voice interview data ready for investment committee review!")

def main():
    """Main function to start real voice interview"""
    print("🎤 REAL VOICE-TO-VOICE INTERVIEW SYSTEM")
    print("=" * 60)
    print("🔊 This system uses your microphone and speakers")
    print("🎯 Designed for: Syed Ubedulla Khadri")
    print("📧 Email: syedubedullakhadri@gmail.com")
    
    # Get founder details
    print(f"\n👋 Welcome! Let's set up your voice interview...")
    
    founder_name = input("👤 Enter your name (or press Enter for 'Syed Ubedulla Khadri'): ").strip()
    if not founder_name:
        founder_name = "Syed Ubedulla Khadri"
    
    startup_name = input("🏢 Enter your startup name (or press Enter for 'TechInnovate'): ").strip()
    if not startup_name:
        startup_name = "TechInnovate"
    
    print(f"\n🚀 Initializing voice interview for {founder_name} from {startup_name}...")
    
    try:
        # Create voice interviewer
        interviewer = RealVoiceInterviewer(founder_name, startup_name)
        
        print(f"\n📋 VOICE INTERVIEW INSTRUCTIONS:")
        print(f"• Speak clearly into your microphone")
        print(f"• Wait for the interviewer to finish speaking before responding")
        print(f"• Say 'stop interview' at any time to end")
        print(f"• The interview covers: business model, market, traction, team, funding")
        print(f"• Duration: Approximately 15-20 minutes")
        
        input(f"\n🎬 Press Enter when you're ready to start the VOICE interview...")
        
        # Start the voice interview
        interviewer.conduct_voice_interview()
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Interview stopped by user.")
    except Exception as e:
        print(f"\n❌ Voice interview error: {str(e)}")
        print("💡 Please check your microphone and speakers are working.")

if __name__ == "__main__":
    main()
