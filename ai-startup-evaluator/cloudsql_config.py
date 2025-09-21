#!/usr/bin/env python3
"""
CloudSQL Configuration Helper
Provides different connection methods for local development and cloud deployment
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

def get_cloudsql_connection_string():
    """Get the appropriate CloudSQL connection string based on environment"""
    
    # Check if we're running in Google Cloud (App Engine, Cloud Run, etc.)
    if os.getenv("GAE_APPLICATION") or os.getenv("K_SERVICE") or os.getenv("CLOUD_RUN_SERVICE"):
        # Running in Google Cloud - use Unix socket
        return "postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db"
    
    # Check if we're running locally with Cloud SQL Proxy
    if os.path.exists("/cloudsql/startup-evaluator-db"):
        # Cloud SQL Proxy is running locally
        return "postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db"
    
    # Check for environment variable override
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    # Default to local SQLite for development
    return "sqlite:///./startup_evaluator.db"

def create_cloudsql_engine():
    """Create SQLAlchemy engine with appropriate CloudSQL configuration"""
    
    connection_string = get_cloudsql_connection_string()
    
    print(f"🔗 Using connection string: {connection_string}")
    
    if connection_string.startswith("sqlite"):
        # SQLite configuration for local development
        return create_engine(
            connection_string,
            connect_args={"check_same_thread": False},
            echo=True if os.getenv("DEBUG") == "true" else False
        )
    elif "cloudsql" in connection_string:
        # CloudSQL configuration
        return create_engine(
            connection_string,
            poolclass=NullPool,
            echo=True if os.getenv("DEBUG") == "true" else False,
            connect_args={
                "sslmode": "disable"  # CloudSQL handles SSL internally
            }
        )
    else:
        # Standard PostgreSQL configuration
        return create_engine(
            connection_string,
            poolclass=NullPool,
            echo=True if os.getenv("DEBUG") == "true" else False
        )

def test_connection():
    """Test the database connection"""
    try:
        engine = create_cloudsql_engine()
        
        with engine.connect() as connection:
            result = connection.execute("SELECT version();")
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"📊 Database version: {version}")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def get_connection_info():
    """Get connection information for debugging"""
    return {
        "connection_string": get_cloudsql_connection_string(),
        "is_cloud": bool(os.getenv("GAE_APPLICATION") or os.getenv("K_SERVICE") or os.getenv("CLOUD_RUN_SERVICE")),
        "has_cloudsql_proxy": os.path.exists("/cloudsql/startup-evaluator-db"),
        "has_env_override": bool(os.getenv("DATABASE_URL"))
    }

if __name__ == "__main__":
    print("🔧 CloudSQL Configuration Helper")
    print("=" * 50)
    
    info = get_connection_info()
    print(f"Connection String: {info['connection_string']}")
    print(f"Running in Cloud: {info['is_cloud']}")
    print(f"CloudSQL Proxy: {info['has_cloudsql_proxy']}")
    print(f"Environment Override: {info['has_env_override']}")
    
    print("\n🧪 Testing connection...")
    test_connection()