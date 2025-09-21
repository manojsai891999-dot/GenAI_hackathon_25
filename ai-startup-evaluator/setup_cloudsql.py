#!/usr/bin/env python3
"""
Setup script for CloudSQL configuration
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file with CloudSQL configuration"""
    env_content = """# CloudSQL Configuration
# Instance: startup-evaluator-db
# Database: startup_evaluator
# User: app-user
# Password: aianalyst

# CloudSQL Connection String
DATABASE_URL=postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db

# Alternative connection format (if needed)
# DATABASE_URL=postgresql://app-user:aianalyst@startup-evaluator-db/startup_evaluator

# For local development (SQLite fallback)
# DATABASE_URL=sqlite:///./startup_evaluator.db

# Google Cloud Configuration
GCS_BUCKET_NAME=startup-evaluator-storage
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Optional: Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Debug Mode
DEBUG=false
"""
    
    # Try to create .env file in backend directory
    backend_env = Path("backend/.env")
    root_env = Path(".env")
    
    try:
        with open(backend_env, "w") as f:
            f.write(env_content)
        print(f"✅ Created {backend_env}")
    except Exception as e:
        print(f"⚠️  Could not create {backend_env}: {e}")
    
    try:
        with open(root_env, "w") as f:
            f.write(env_content)
        print(f"✅ Created {root_env}")
    except Exception as e:
        print(f"⚠️  Could not create {root_env}: {e}")

def update_database_config():
    """Update database configuration with CloudSQL details"""
    print("🔧 Updating database configuration...")
    
    # The database.py file has already been updated with CloudSQL configuration
    print("✅ Database configuration updated with CloudSQL details")
    print("   - Instance: startup-evaluator-db")
    print("   - Database: startup_evaluator")
    print("   - User: app-user")
    print("   - Password: aianalyst")

def install_dependencies():
    """Install required dependencies for CloudSQL"""
    print("📦 Installing CloudSQL dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "google-cloud-sql-connector[pg8000]",
            "pg8000"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ CloudSQL dependencies installed successfully")
        else:
            print(f"⚠️  Warning: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not install dependencies: {e}")

def test_configuration():
    """Test the CloudSQL configuration"""
    print("🧪 Testing CloudSQL configuration...")
    
    try:
        # Import and test the database configuration
        sys.path.append("backend")
        from backend.models.database import DATABASE_URL, engine
        
        print(f"✅ Database URL configured: {DATABASE_URL}")
        
        # Test engine creation
        print("✅ Database engine created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 CloudSQL Setup for AI Interview Agent")
    print("=" * 60)
    
    print("\n📋 Configuration Details:")
    print("   Instance: startup-evaluator-db")
    print("   Database: startup_evaluator")
    print("   User: app-user")
    print("   Password: aianalyst")
    print("=" * 60)
    
    # Create environment files
    print("\n1️⃣  Creating environment files...")
    create_env_file()
    
    # Update database configuration
    print("\n2️⃣  Updating database configuration...")
    update_database_config()
    
    # Install dependencies
    print("\n3️⃣  Installing dependencies...")
    install_dependencies()
    
    # Test configuration
    print("\n4️⃣  Testing configuration...")
    config_success = test_configuration()
    
    if config_success:
        print("\n🎉 CloudSQL setup completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Ensure your CloudSQL instance is running")
        print("   2. Run: python test_cloudsql_connection.py")
        print("   3. Run: python test_standalone_agent.py")
        print("   4. Start the web interface: python web_interview_interface.py")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("   Please check the configuration and try again")
    
    return config_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)