#!/usr/bin/env python3
"""
Simplified agent test without ADK dependencies
"""

import os
import sys
import json
from pathlib import Path

def test_agent_structure():
    """Test the agent structure without ADK dependencies"""
    print("🧪 Testing agent structure...")
    
    try:
        # Set environment variable for local testing
        os.environ["DATABASE_URL"] = "sqlite:///./test_startup_evaluator.db"
        
        # Test importing the main components
        sys.path.append("backend")
        
        # Test database models
        from backend.models.database import DATABASE_URL, create_tables
        print("✅ Database configuration loaded")
        print(f"   Database URL: {DATABASE_URL}")
        
        # Test schemas
        from backend.models.schemas import InterviewSession, InterviewResponse
        print("✅ Database schemas loaded")
        
        # Test GCS service
        from backend.services.gcs_service import gcs_service
        print("✅ GCS service loaded")
        
        # Test interview questions
        from standalone_interview_agent import INVESTMENT_QUESTIONS
        print(f"✅ Interview questions loaded: {len(INVESTMENT_QUESTIONS)} questions")
        
        # Test standalone agent
        from standalone_interview_agent import interview_agent
        print("✅ Standalone interview agent loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False

def test_agent_functionality():
    """Test basic agent functionality"""
    print("\n🔧 Testing agent functionality...")
    
    try:
        from standalone_interview_agent import interview_agent
        
        # Test starting a session
        result = interview_agent.start_interview_session("Test Founder", "Test Startup")
        
        if result["status"] == "success":
            print("✅ Session creation works")
            session_id = result["session_id"]
            
            # Test processing a response
            response_result = interview_agent.process_founder_response(
                result["session_data"],
                "We're solving food waste in supply chains with AI-powered demand forecasting."
            )
            
            if response_result["status"] == "success":
                print("✅ Response processing works")
                print(f"   Next message: {response_result['next_message'][:100]}...")
                print(f"   Analysis: Sentiment={response_result['analysis']['sentiment_score']:.2f}, Confidence={response_result['analysis']['confidence_score']:.2f}")
                return True
            else:
                print(f"❌ Response processing failed: {response_result.get('error_message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Session creation failed: {result.get('error_message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n🗄️ Testing database operations...")
    
    try:
        # Set environment variable for local testing
        os.environ["DATABASE_URL"] = "sqlite:///./test_startup_evaluator.db"
        
        from backend.models.database import create_tables, get_db
        from backend.models.schemas import InterviewSession, InterviewResponse
        
        # Create tables
        create_tables()
        print("✅ Database tables created")
        
        # Test session creation
        with next(get_db()) as db:
            test_session = InterviewSession(
                session_id="deployment_test_123",
                founder_name="Deployment Test",
                startup_name="Test Startup",
                session_status="active"
            )
            db.add(test_session)
            db.commit()
            print("✅ Test session created in database")
            
            # Test response creation
            test_response = InterviewResponse(
                session_id="deployment_test_123",
                founder_name="Deployment Test",
                question="What problem are you solving?",
                response="We're solving food waste in supply chains",
                question_category="problem",
                sentiment_score=0.8,
                confidence_score=0.9
            )
            db.add(test_response)
            db.commit()
            print("✅ Test response created in database")
            
            # Clean up
            db.query(InterviewResponse).filter(InterviewResponse.session_id == "deployment_test_123").delete()
            db.query(InterviewSession).filter(InterviewSession.session_id == "deployment_test_123").delete()
            db.commit()
            print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ADK Interview Agent - Simplified Test")
    print("=" * 50)
    
    # Test agent structure
    if not test_agent_structure():
        print("\n❌ Agent structure test failed")
        return False
    
    # Test database operations
    if not test_database_operations():
        print("\n❌ Database test failed")
        return False
    
    # Test agent functionality
    if not test_agent_functionality():
        print("\n❌ Agent functionality test failed")
        return False
    
    print("\n🎉 All tests passed!")
    print("✅ The agent is ready for deployment")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)