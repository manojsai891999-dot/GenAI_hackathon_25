#!/usr/bin/env python3
"""
Simplified test for the ADK Interview Agent
Tests core functionality without external dependencies
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_schema():
    """Test database schema creation"""
    print("🗄️  Testing Database Schema")
    print("=" * 40)
    
    try:
        from backend.models.database import create_tables
        from backend.models.schemas import InterviewSession, InterviewResponse
        
        # Create tables
        create_tables()
        print("✅ Database tables created successfully")
        
        # Test session creation
        from backend.models.database import get_db
        with next(get_db()) as db:
            test_session = InterviewSession(
                session_id="test_session_123",
                founder_name="Test Founder",
                startup_name="Test Startup",
                session_status="active"
            )
            db.add(test_session)
            db.commit()
            print("✅ Test session created in database")
            
            # Test response creation
            test_response = InterviewResponse(
                session_id="test_session_123",
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
        import traceback
        traceback.print_exc()
        return False

def test_gcs_service():
    """Test GCS service (without actual upload)"""
    print("\n☁️  Testing GCS Service")
    print("=" * 40)
    
    try:
        from backend.services.gcs_service import GCSService
        
        # Test service initialization
        gcs_service = GCSService()
        print("✅ GCS service initialized")
        
        # Test helper functions
        from backend.services.gcs_service import get_startup_folder_path, get_memo_path
        
        startup_id = 123
        folder_path = get_startup_folder_path(startup_id)
        memo_path = get_memo_path(startup_id)
        
        print(f"✅ Helper functions work: {folder_path}, {memo_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ GCS test failed: {str(e)}")
        print("💡 Note: GCS test requires proper Google Cloud credentials")
        return False

def test_interview_agent_core():
    """Test core interview agent functionality without ADK"""
    print("\n🤖 Testing Interview Agent Core")
    print("=" * 40)
    
    try:
        # Test predefined questions
        from backend.agents.adk_interview_agent import INVESTMENT_QUESTIONS
        
        print(f"✅ Found {len(INVESTMENT_QUESTIONS)} predefined questions")
        
        for i, question in enumerate(INVESTMENT_QUESTIONS, 1):
            print(f"   {i}. {question['question']} ({question['category']})")
        
        # Test analysis functions
        from backend.agents.adk_interview_agent import InterviewAgent
        
        agent = InterviewAgent()
        
        # Test sentiment calculation
        test_response = "We're very excited about our growth prospects and confident in our business model."
        sentiment = agent._calculate_sentiment(test_response)
        print(f"✅ Sentiment calculation: {sentiment:.2f}")
        
        # Test confidence calculation
        confidence = agent._calculate_confidence(test_response)
        print(f"✅ Confidence calculation: {confidence:.2f}")
        
        # Test insight extraction
        insights = agent._extract_insights(test_response, "traction")
        print(f"✅ Insight extraction: {insights}")
        
        # Test red flag identification
        red_flags = agent._identify_red_flags("I don't know", "traction")
        print(f"✅ Red flag identification: {red_flags}")
        
        # Test positive signal identification
        positive_signals = agent._identify_positive_signals(test_response, "traction")
        print(f"✅ Positive signal identification: {positive_signals}")
        
        return True
        
    except Exception as e:
        print(f"❌ Interview agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generation():
    """Test report generation functionality"""
    print("\n📊 Testing Report Generation")
    print("=" * 40)
    
    try:
        from backend.agents.adk_interview_agent import InterviewAgent
        
        agent = InterviewAgent()
        
        # Create mock session data
        session_data = {
            "session_id": "test_session_456",
            "founder_name": "Test Founder",
            "startup_name": "Test Startup"
        }
        
        # Create mock memory data
        memory_data = {
            "insights_gathered": {"market validation": 2, "strong team": 1},
            "red_flags": ["limited traction", "high competition"],
            "positive_signals": ["detailed responses", "data-driven approach"]
        }
        
        # Test report generation
        report = agent._generate_summary_report(session_data, memory_data)
        
        print("✅ Report generation successful")
        print(f"   Founder: {report['interview_summary']['founder_name']}")
        print(f"   Startup: {report['interview_summary']['startup_name']}")
        print(f"   Strengths: {len(report['key_insights']['strengths'])}")
        print(f"   Risks: {len(report['key_insights']['risks'])}")
        print(f"   Recommendation: {report['overall_assessment']['recommendation']}")
        
        # Test text summary generation
        text_summary = agent._generate_text_summary(report)
        print(f"✅ Text summary generated ({len(text_summary)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_web_interface():
    """Test web interface components"""
    print("\n🌐 Testing Web Interface")
    print("=" * 40)
    
    try:
        # Test Flask app creation
        from web_interview_interface import app
        
        print("✅ Flask app created successfully")
        
        # Test template existence
        template_path = "templates/interview_interface.html"
        if os.path.exists(template_path):
            print("✅ HTML template exists")
        else:
            print("❌ HTML template not found")
            return False
        
        # Test static content
        with open(template_path, 'r') as f:
            content = f.read()
            if "AI Interview Agent" in content:
                print("✅ Template contains expected content")
            else:
                print("❌ Template missing expected content")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web interface test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 ADK Interview Agent Test Suite")
    print("=" * 60)
    
    tests = [
        ("Database Schema", test_database_schema),
        ("GCS Service", test_gcs_service),
        ("Interview Agent Core", test_interview_agent_core),
        ("Report Generation", test_report_generation),
        ("Web Interface", test_web_interface)
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
        print("🎉 All tests passed! The ADK Interview Agent is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)