#!/usr/bin/env python3
"""
Test CloudSQL connection with the provided instance details
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_cloudsql_connection():
    """Test connection to CloudSQL instance"""
    print("🔗 Testing CloudSQL Connection")
    print("=" * 50)
    
    # CloudSQL connection details
    instance_name = "startup-evaluator-db"
    database_name = "startup_evaluator"
    username = "app-user"
    password = "aianalyst"
    
    print(f"Instance: {instance_name}")
    print(f"Database: {database_name}")
    print(f"User: {username}")
    print("=" * 50)
    
    # Test different connection string formats
    connection_strings = [
        # Unix socket connection (recommended for CloudSQL)
        f"postgresql://{username}:{password}@/{database_name}?host=/cloudsql/{instance_name}",
        
        # TCP connection (if Unix socket not available)
        f"postgresql://{username}:{password}@{instance_name}/{database_name}",
        
        # With explicit port
        f"postgresql://{username}:{password}@{instance_name}:5432/{database_name}",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n🧪 Testing Connection String {i}:")
        print(f"   {conn_str}")
        
        try:
            # Create engine
            engine = create_engine(
                conn_str,
                poolclass=None,  # No connection pooling for testing
                echo=False
            )
            
            # Test connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"   ✅ Connection successful!")
                print(f"   📊 PostgreSQL version: {version}")
                
                # Test database access
                result = connection.execute(text("SELECT current_database();"))
                current_db = result.fetchone()[0]
                print(f"   📁 Current database: {current_db}")
                
                # Test table creation (if needed)
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"   📋 Existing tables: {tables}")
                
                return True
                
        except SQLAlchemyError as e:
            print(f"   ❌ Connection failed: {str(e)}")
            continue
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
            continue
    
    print(f"\n❌ All connection attempts failed")
    return False

def test_database_operations():
    """Test basic database operations"""
    print(f"\n🗄️  Testing Database Operations")
    print("=" * 50)
    
    try:
        from backend.models.database import get_db, create_tables
        from backend.models.schemas import InterviewSession, InterviewResponse
        
        # Create tables
        print("Creating database tables...")
        create_tables()
        print("✅ Tables created successfully")
        
        # Test session creation
        with next(get_db()) as db:
            test_session = InterviewSession(
                session_id="cloudsql_test_123",
                founder_name="Test Founder",
                startup_name="Test Startup",
                session_status="active"
            )
            db.add(test_session)
            db.commit()
            print("✅ Test session created in CloudSQL")
            
            # Test response creation
            test_response = InterviewResponse(
                session_id="cloudsql_test_123",
                founder_name="Test Founder",
                question="What problem are you solving?",
                response="We're solving food waste in supply chains",
                question_category="problem",
                sentiment_score=0.8,
                confidence_score=0.9
            )
            db.add(test_response)
            db.commit()
            print("✅ Test response created in CloudSQL")
            
            # Verify data
            session_count = db.query(InterviewSession).count()
            response_count = db.query(InterviewResponse).count()
            print(f"✅ CloudSQL contains {session_count} sessions and {response_count} responses")
            
            # Clean up test data
            db.query(InterviewResponse).filter(InterviewResponse.session_id == "cloudsql_test_123").delete()
            db.query(InterviewSession).filter(InterviewSession.session_id == "cloudsql_test_123").delete()
            db.commit()
            print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run CloudSQL connection tests"""
    print("🧪 CloudSQL Connection Test Suite")
    print("=" * 60)
    
    # Test basic connection
    connection_success = test_cloudsql_connection()
    
    if connection_success:
        # Test database operations
        operations_success = test_database_operations()
        
        if operations_success:
            print(f"\n🎉 All CloudSQL tests passed!")
            print(f"✅ Connection to startup-evaluator-db successful")
            print(f"✅ Database startup_evaluator accessible")
            print(f"✅ User app-user authenticated")
            print(f"✅ CRUD operations working")
        else:
            print(f"\n⚠️  Connection successful but database operations failed")
    else:
        print(f"\n❌ CloudSQL connection failed")
        print(f"💡 Please check:")
        print(f"   - CloudSQL instance is running")
        print(f"   - Network connectivity")
        print(f"   - Authentication credentials")
        print(f"   - Firewall rules")
    
    return connection_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)