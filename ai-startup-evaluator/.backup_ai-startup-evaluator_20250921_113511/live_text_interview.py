#!/usr/bin/env python3
"""
Live Text-based Interview System
Conducts real-time text interviews with startup founders
(Simulates voice interview through text input/output)
"""

import os
import sys
import json
import time
from datetime import datetime

class LiveTextInterviewer:
    """Real-time text-based interview system"""
    
    def __init__(self, founder_name="Syed Ubedulla Khadri", startup_name="Your Startup"):
        self.founder_name = founder_name
        self.startup_name = startup_name
        
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
        
        print("🎤 Initializing live interview system...")
        print("💡 This is a text-based simulation of voice interview")
    
    def speak(self, text):
        """Display interviewer's message (simulates text-to-speech)"""
        print(f"\n🎤 INTERVIEWER:")
        print("=" * 50)
        
        # Simulate typing effect for more natural feel
        words = text.split()
        for i, word in enumerate(words):
            print(word, end=" ", flush=True)
            if i % 8 == 7:  # New line every 8 words for readability
                print()
            time.sleep(0.1)  # Small delay to simulate speaking
        
        print("\n" + "=" * 50)
        print("🎙️  Your turn to respond...")
    
    def listen_for_response(self):
        """Get founder's text response (simulates speech recognition)"""
        print(f"\n👤 {self.founder_name}, please type your response:")
        print("💡 Type 'stop interview' to end the session")
        print("📝 Your response: ", end="")
        
        try:
            response = input().strip()
            
            if response.lower() in ['stop interview', 'stop', 'quit', 'exit']:
                return "STOP_INTERVIEW"
            
            if not response:
                print("❌ Empty response. Please provide an answer.")
                return None
            
            return response
            
        except KeyboardInterrupt:
            return "STOP_INTERVIEW"
        except Exception as e:
            print(f"❌ Input error: {str(e)}")
            return None
    
    def analyze_response(self, response_text):
        """Analyze founder's response for insights and sentiment"""
        if not response_text:
            return {"quality_score": 0, "sentiment_score": 0.5, "insights": {}}
        
        word_count = len(response_text.split())
        
        # Sentiment analysis
        positive_words = ["excited", "fantastic", "great", "amazing", "successful", "growing", 
                         "confident", "passionate", "love", "excellent", "strong", "profitable"]
        negative_words = ["challenging", "difficult", "struggling", "worried", "concerned", 
                         "problem", "issue", "hard", "tough", "failing"]
        
        positive_count = sum(1 for word in positive_words if word.lower() in response_text.lower())
        negative_count = sum(1 for word in negative_words if word.lower() in response_text.lower())
        
        sentiment_score = 0.5  # neutral
        if positive_count + negative_count > 0:
            sentiment_score = positive_count / (positive_count + negative_count)
        
        # Extract business insights
        insights = {}
        business_keywords = {
            "revenue": ["revenue", "money", "income", "sales", "profit", "pricing", "$"],
            "customers": ["customers", "clients", "users", "market", "customer"],
            "team": ["team", "founder", "employees", "hiring", "ceo", "cto"],
            "funding": ["funding", "investment", "capital", "raise", "investor"],
            "growth": ["growth", "growing", "scale", "expansion", "traction"],
            "product": ["product", "platform", "technology", "software", "ai"],
            "competition": ["competitors", "competition", "differentiate", "advantage"]
        }
        
        for category, keywords in business_keywords.items():
            if any(keyword in response_text.lower() for keyword in keywords):
                insights[category] = True
        
        # Quality score based on length and specificity
        length_score = min(word_count / 50, 1.0)  # Optimal around 50 words
        specificity_score = len(insights) / len(business_keywords)  # How many topics covered
        
        quality_score = (length_score * 0.4 + sentiment_score * 0.3 + specificity_score * 0.3)
        
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
            self.session_data["rapport_level"] = min(self.session_data["rapport_level"] + 0.15, 1.0)
        elif response_analysis["quality_score"] > 0.5:
            self.session_data["rapport_level"] = min(self.session_data["rapport_level"] + 0.05, 1.0)
        
        # Generate enthusiastic responses based on sentiment
        enthusiasm_prefix = ""
        if response_analysis["sentiment_score"] > 0.7:
            enthusiasm_prefix = "That's fantastic! "
        elif response_analysis["sentiment_score"] > 0.5:
            enthusiasm_prefix = "That sounds great! "
        
        # Topic-based questions with natural transitions
        topic_questions = {
            "introduction": {
                "next_topic": "business_model",
                "question": f"{enthusiasm_prefix}Thanks for sharing that background, {founder_name}! I'm really excited to learn more about {startup_name}. Now let's dive into the business mechanics - how exactly do you make money? What's your revenue model and pricing strategy?"
            },
            "business_model": {
                "next_topic": "market_opportunity", 
                "question": f"{enthusiasm_prefix}That business model makes sense! Now I'm curious about the market you're targeting. How big is this opportunity? Who are your main competitors and how do you differentiate from them?"
            },
            "market_opportunity": {
                "next_topic": "traction_metrics",
                "question": f"{enthusiasm_prefix}The market opportunity sounds compelling! Let's talk about your traction. What does your growth look like? Can you share some key metrics, customer numbers, or success stories?"
            },
            "traction_metrics": {
                "next_topic": "team_execution",
                "question": f"{enthusiasm_prefix}Those are encouraging numbers! Tell me about the team behind this success. What's your background? Who are your co-founders? How are you thinking about scaling the team?"
            },
            "team_execution": {
                "next_topic": "funding_vision",
                "question": f"{enthusiasm_prefix}Sounds like you have a strong foundation! Looking ahead, what are your funding needs? How much are you raising and what will you use it for? What's your long-term vision for {startup_name}?"
            },
            "funding_vision": {
                "next_topic": "conclusion",
                "question": f"{enthusiasm_prefix}That's an exciting vision, {founder_name}! Before we wrap up, what questions do you have for me? What would you like to know about our investment process or what we typically look for in startups?"
            }
        }
        
        if current_topic in topic_questions:
            transition = topic_questions[current_topic]
            self.session_data["current_topic"] = transition["next_topic"]
            return transition["question"]
        else:
            return f"Thank you so much for this conversation, {founder_name}! This has been really insightful learning about {startup_name}. We'll review everything and be in touch soon with next steps. I'm excited about what you're building!"
    
    def show_real_time_analysis(self, analysis):
        """Display real-time analysis of the conversation"""
        print(f"\n📊 REAL-TIME ANALYSIS:")
        print("-" * 30)
        print(f"🎯 Current Topic: {self.session_data['current_topic'].replace('_', ' ').title()}")
        print(f"🤝 Rapport Level: {self.session_data['rapport_level']:.2f} ({'Excellent' if self.session_data['rapport_level'] > 0.8 else 'Good' if self.session_data['rapport_level'] > 0.6 else 'Building'})")
        print(f"📝 Response Quality: {analysis['quality_score']:.2f} ({'High' if analysis['quality_score'] > 0.7 else 'Medium' if analysis['quality_score'] > 0.4 else 'Low'})")
        print(f"😊 Sentiment: {analysis['sentiment_score']:.2f} ({'Positive' if analysis['sentiment_score'] > 0.6 else 'Neutral' if analysis['sentiment_score'] > 0.4 else 'Negative'})")
        print(f"💡 Key Topics: {', '.join(analysis['insights'].keys()) if analysis['insights'] else 'None detected'}")
        print(f"📊 Word Count: {analysis['word_count']} words")
    
    def conduct_live_interview(self):
        """Conduct the complete live text interview"""
        print("\n🚀 STARTING LIVE INTERVIEW")
        print("=" * 60)
        print(f"👤 Founder: {self.founder_name}")
        print(f"🏢 Startup: {self.startup_name}")
        print(f"📋 Session: {self.session_data['session_id']}")
        print(f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Opening message
        opening_message = f"""Hi {self.founder_name}! Welcome to your live interview session. 
        
I'm really excited to learn about {self.startup_name} and what you're building. This will be a natural conversation where we'll explore your business model, market opportunity, traction, team, and vision.

Just respond naturally to my questions - I'll ask follow-up questions based on your answers. The whole conversation should take about 15-20 minutes.

To get started, could you tell me a bit about yourself and what inspired you to start {self.startup_name}? What problem are you solving and why is it important?"""
        
        self.speak(opening_message)
        
        # Main interview loop
        exchange_count = 0
        max_exchanges = 6  # Limit to prevent overly long interviews
        
        while self.session_data["interview_active"] and exchange_count < max_exchanges:
            exchange_count += 1
            print(f"\n🔄 EXCHANGE {exchange_count}/{max_exchanges}")
            
            # Listen for founder's response
            response = self.listen_for_response()
            
            if response == "STOP_INTERVIEW":
                self.speak(f"Thank you for the interview, {self.founder_name}! It was great talking with you about {self.startup_name}.")
                break
            elif response is None:
                print("⚠️  Let me rephrase the question...")
                continue
            
            # Analyze the response
            analysis = self.analyze_response(response)
            
            # Show real-time analysis
            self.show_real_time_analysis(analysis)
            
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
            
            # Check if we've reached conclusion
            if self.session_data["current_topic"] == "conclusion":
                self.speak(next_question)
                
                # Final response
                final_response = self.listen_for_response()
                if final_response and final_response != "STOP_INTERVIEW":
                    closing_message = f"""Perfect! Thank you so much for your time, {self.founder_name}. 
                    
This has been a fantastic conversation about {self.startup_name}. I'm really impressed with what you're building and your vision for the future.

We'll review everything from our conversation today and get back to you with next steps within 48 hours. Based on what I've heard, I'm excited to continue the conversation with our investment team.

Have a great day, and thank you again for sharing your story with us!"""
                    
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
        
        print(f"\n🎉 INTERVIEW COMPLETED!")
        print("=" * 60)
        print(f"📊 INTERVIEW SUMMARY:")
        print(f"   ⏱️  Duration: {duration.seconds // 60} minutes, {duration.seconds % 60} seconds")
        print(f"   💬 Total Exchanges: {len(self.session_data['conversation_history']) // 2}")
        print(f"   🤝 Final Rapport Level: {self.session_data['rapport_level']:.2f}")
        print(f"   🎯 Topics Covered: {self.session_data['current_topic'].replace('_', ' ').title()}")
        print(f"   💡 Key Business Areas Discussed: {', '.join(self.session_data['insights_gathered'].keys())}")
        
        print(f"\n📋 SESSION DETAILS:")
        print(f"   🆔 Session ID: {self.session_data['session_id']}")
        print(f"   👤 Founder: {self.founder_name}")
        print(f"   🏢 Startup: {self.startup_name}")
        print(f"   📅 Date: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Investment recommendation based on rapport and insights
        recommendation = "Strong Interest"
        if self.session_data['rapport_level'] > 0.8 and len(self.session_data['insights_gathered']) >= 5:
            recommendation = "High Interest - Recommend Next Steps"
        elif self.session_data['rapport_level'] > 0.6 and len(self.session_data['insights_gathered']) >= 3:
            recommendation = "Moderate Interest - Further Evaluation"
        elif self.session_data['rapport_level'] < 0.5 or len(self.session_data['insights_gathered']) < 2:
            recommendation = "Limited Interest - Pass"
        
        print(f"\n🎯 PRELIMINARY ASSESSMENT:")
        print(f"   📈 Investment Interest Level: {recommendation}")
        print(f"   ✅ Interview data ready for detailed evaluation!")

def main():
    """Main function to start live interview"""
    print("🎤 LIVE INTERVIEW SYSTEM")
    print("=" * 50)
    print("💡 Text-based simulation of voice interview")
    print("🎯 Designed for: syedubedullakhadri@gmail.com")
    
    # Get founder details
    print(f"\n👋 Welcome! Let's set up your interview...")
    
    founder_name = input("👤 Enter your name (or press Enter for 'Syed Ubedulla Khadri'): ").strip()
    if not founder_name:
        founder_name = "Syed Ubedulla Khadri"
    
    startup_name = input("🏢 Enter your startup name (or press Enter for 'TechInnovate'): ").strip()
    if not startup_name:
        startup_name = "TechInnovate"
    
    print(f"\n🚀 Initializing interview for {founder_name} from {startup_name}...")
    
    try:
        # Create and start interview
        interviewer = LiveTextInterviewer(founder_name, startup_name)
        
        print(f"\n📝 INSTRUCTIONS:")
        print(f"• This is a live, interactive interview")
        print(f"• Respond naturally to questions as if talking to an investor")
        print(f"• Type 'stop interview' at any time to end")
        print(f"• The interview covers: business model, market, traction, team, funding")
        
        input(f"\n🎬 Press Enter when you're ready to start the live interview...")
        interviewer.conduct_live_interview()
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Interview stopped by user.")
    except Exception as e:
        print(f"\n❌ Interview error: {str(e)}")

if __name__ == "__main__":
    main()
