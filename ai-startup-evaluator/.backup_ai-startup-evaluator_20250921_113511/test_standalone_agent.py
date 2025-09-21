#!/usr/bin/env python3
"""
Test script for the Standalone Interview Agent
Tests the complete interview workflow without external dependencies
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from standalone_interview_agent import interview_agent, INVESTMENT_QUESTIONS

def test_interview_workflow():
    """Test the complete interview workflow"""
    print("🚀 Testing Standalone Interview Agent Workflow")
    print("=" * 60)
    
    # Test data
    founder_name = "Sarah Johnson"
    startup_name = "EcoTech Solutions"
    
    print(f"👤 Founder: {founder_name}")
    print(f"🏢 Startup: {startup_name}")
    print("=" * 60)
    
    try:
        # Step 1: Start interview session
        print("\n📋 Step 1: Starting interview session...")
        session_result = interview_agent.start_interview_session(founder_name, startup_name)
        
        if session_result["status"] != "success":
            print(f"❌ Failed to start session: {session_result['error_message']}")
            return False
        
        print(f"✅ Session started successfully!")
        print(f"🆔 Session ID: {session_result['session_id']}")
        print(f"📊 Total Questions: {session_result['total_questions']}")
        
        # Display greeting
        print(f"\n🎤 INTERVIEWER GREETING:")
        print("-" * 40)
        print(session_result['greeting'])
        
        # Step 2: Simulate interview responses
        print(f"\n🎭 Step 2: Simulating interview responses...")
        
        # Sample responses for each question category
        sample_responses = [
            {
                "response": "We're solving the critical problem of food waste in the supply chain. Currently, 40% of all food produced globally goes to waste, costing the economy $1.3 trillion annually. Our AI-powered platform helps grocery stores and restaurants predict demand more accurately, reducing waste by up to 30% while increasing profitability.",
                "context": "Problem definition with market size"
            },
            {
                "response": "Our primary customers are mid-to-large grocery store chains and restaurant groups. We're currently working with 15 grocery chains across the West Coast, including Whole Foods and Safeway. We also have 8 restaurant groups as clients. Our target is chains with 50+ locations and $100M+ annual revenue.",
                "context": "Target customer identification"
            },
            {
                "response": "We've grown from 0 to 15 grocery clients in 18 months, generating $2.1M ARR. Our monthly recurring revenue is growing at 25% month-over-month. We've reduced food waste by an average of 28% for our clients, saving them $3.2M collectively. Customer retention is 100% and our average contract value has increased from $8K to $15K monthly.",
                "context": "Strong traction metrics"
            },
            {
                "response": "We use a SaaS subscription model with three tiers: Basic ($2,500/month), Professional ($7,500/month), and Enterprise ($15,000/month). We also take 2% of the waste reduction savings as a performance bonus. Our gross margins are 85% and we're targeting 90% by optimizing our AI infrastructure costs.",
                "context": "Clear business model with pricing"
            },
            {
                "response": "Our main competitors are Spoiler Alert and LeanPath, but they focus on waste tracking rather than prevention. We're the only platform that uses real-time demand forecasting to prevent waste before it happens. Our AI models are trained on 5 years of industry data and we have 3 patents pending on our predictive algorithms.",
                "context": "Competitive differentiation"
            },
            {
                "response": "We're raising $8M Series A to scale our sales team and expand to the East Coast. The funds will be used for: 40% sales and marketing to acquire 50+ new clients, 30% product development for new AI features, 20% team expansion to hire 12 engineers, and 10% working capital. We expect this to last 18 months and get us to $10M ARR.",
                "context": "Detailed fundraising plan"
            }
        ]
        
        session_data = session_result['session_data']
        conversation_log = []
        
        # Process each response
        for i, sample in enumerate(sample_responses):
            print(f"\n--- Question {i+1}: {sample['context']} ---")
            print(f"👤 FOUNDER ({founder_name}): {sample['response']}")
            
            # Process the response
            result = interview_agent.process_founder_response(session_data, sample['response'])
            
            if result["status"] == "success":
                print(f"🎤 INTERVIEWER: {result['next_message']}")
                
                # Show analysis
                analysis = result['analysis']
                print(f"\n📊 Analysis:")
                print(f"   🎯 Category: {result['current_category'].replace('_', ' ').title()}")
                print(f"   😊 Sentiment: {analysis['sentiment_score']:.2f}")
                print(f"   🎯 Confidence: {analysis['confidence_score']:.2f}")
                print(f"   💡 Insights: {', '.join(analysis['key_insights'][:3])}")
                if analysis['red_flags']:
                    print(f"   ⚠️  Red Flags: {', '.join(analysis['red_flags'])}")
                if analysis['positive_signals']:
                    print(f"   ✅ Positive: {', '.join(analysis['positive_signals'])}")
                
                # Show progress
                progress = result['progress']
                print(f"   📈 Progress: {progress['progress_percentage']}% complete")
                
                conversation_log.append({
                    "question": i + 1,
                    "founder_response": sample['response'],
                    "interviewer_response": result['next_message'],
                    "analysis": analysis,
                    "progress": progress
                })
                
                # Small delay to simulate real conversation
                time.sleep(0.5)
            else:
                print(f"❌ Error processing response: {result['error_message']}")
                break
        
        # Step 3: Complete interview and generate report
        print(f"\n📋 Step 3: Completing interview and generating report...")
        
        # The interview should be completed after processing all responses
        # Let's manually trigger completion for testing
        final_result = interview_agent.process_founder_response(session_data, "Thank you for the comprehensive interview. I believe we've covered all the key areas.")
        
        if final_result.get("interview_completed"):
            print(f"✅ Interview completed successfully!")
            print(f"📊 Summary Report Generated")
            print(f"☁️  GCS Path: {final_result.get('gcs_path', 'N/A')}")
            
            # Display summary
            if 'summary_report' in final_result:
                report = final_result['summary_report']
                print(f"\n📋 INTERVIEW SUMMARY REPORT")
                print("=" * 50)
                print(f"Founder: {report['interview_summary']['founder_name']}")
                print(f"Startup: {report['interview_summary']['startup_name']}")
                print(f"Questions Answered: {report['interview_summary']['total_questions']}")
                print(f"Overall Sentiment: {report['overall_assessment']['sentiment_score']:.2f}")
                print(f"Overall Confidence: {report['overall_assessment']['confidence_score']:.2f}")
                print(f"Recommendation: {report['overall_assessment']['recommendation']}")
                
                print(f"\n💡 Key Strengths:")
                for strength in report['key_insights']['strengths'][:5]:
                    print(f"   - {strength}")
                
                print(f"\n⚠️  Risks Identified:")
                for risk in report['key_insights']['risks'][:3]:
                    print(f"   - {risk}")
                
                print(f"\n🎯 Next Steps:")
                for step in report['overall_assessment']['next_steps'][:3]:
                    print(f"   - {step}")
        
        print(f"\n✅ Test completed successfully!")
        print(f"📊 Total Exchanges: {len(conversation_log)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_functions():
    """Test individual analysis functions"""
    print("\n🔍 Testing Analysis Functions")
    print("=" * 40)
    
    try:
        # Test sentiment calculation
        test_responses = [
            "We're very excited about our growth prospects and confident in our business model.",
            "This is challenging and we're struggling with some aspects.",
            "We have proven results and validated our approach with data."
        ]
        
        for response in test_responses:
            sentiment = interview_agent._calculate_sentiment(response)
            confidence = interview_agent._calculate_confidence(response)
            print(f"Response: {response[:50]}...")
            print(f"  Sentiment: {sentiment:.2f}, Confidence: {confidence:.2f}")
        
        # Test insight extraction
        test_cases = [
            ("We're solving a $1.3B market problem", "problem"),
            ("Our enterprise customers love our solution", "customers"),
            ("We've grown 25% month-over-month", "traction"),
            ("We use a SaaS subscription model at $2,500/month", "business_model"),
            ("We're different from competitors with our AI approach", "competition"),
            ("We're raising $8M Series A", "fundraising")
        ]
        
        for response, category in test_cases:
            insights = interview_agent._extract_insights(response, category)
            red_flags = interview_agent._identify_red_flags(response, category)
            positive_signals = interview_agent._identify_positive_signals(response, category)
            
            print(f"\nCategory: {category}")
            print(f"  Insights: {insights}")
            print(f"  Red Flags: {red_flags}")
            print(f"  Positive Signals: {positive_signals}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis functions test failed: {str(e)}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n🗄️  Testing Database Operations")
    print("=" * 40)
    
    try:
        from backend.models.database import get_db
        from backend.models.schemas import InterviewSession, InterviewResponse
        
        # Test session creation
        with next(get_db()) as db:
            test_session = InterviewSession(
                session_id="test_standalone_123",
                founder_name="Test Founder",
                startup_name="Test Startup",
                session_status="active"
            )
            db.add(test_session)
            db.commit()
            print("✅ Test session created in database")
            
            # Test response creation
            test_response = InterviewResponse(
                session_id="test_standalone_123",
                founder_name="Test Founder",
                question="What problem are you solving?",
                response="We're solving food waste in supply chains",
                question_category="problem",
                sentiment_score=0.8,
                confidence_score=0.9
            )
            db.add(test_response)
            db.commit()
            print("✅ Test response created in database")
            
            # Verify data
            session_count = db.query(InterviewSession).count()
            response_count = db.query(InterviewResponse).count()
            print(f"✅ Database contains {session_count} sessions and {response_count} responses")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Standalone Interview Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Operations", test_database_operations),
        ("Analysis Functions", test_analysis_functions),
        ("Complete Workflow", test_interview_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Standalone Interview Agent is ready to use.")
        print("\n📚 Usage:")
        print("   from standalone_interview_agent import interview_agent")
        print("   result = interview_agent.start_interview_session('Founder Name', 'Startup Name')")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)