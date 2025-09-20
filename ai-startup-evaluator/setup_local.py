#!/usr/bin/env python3
"""
Local setup script for AI Startup Evaluator
This script sets up the local development environment with SQLite
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Error: {e.stderr}")
        return None

def setup_backend():
    """Set up the backend environment"""
    print("\n🔧 Setting up Backend...")
    
    backend_dir = Path("backend")
    
    # Install Python dependencies
    print("Installing Python dependencies...")
    run_command("pip install -r requirements.txt", cwd=backend_dir)
    
    # Create database tables
    print("Creating database tables...")
    create_db_script = """
import sys
sys.path.append('.')
from models.database import create_tables
create_tables()
print("Database tables created successfully!")
"""
    
    with open(backend_dir / "create_db.py", "w") as f:
        f.write(create_db_script)
    
    run_command("python create_db.py", cwd=backend_dir)
    
    # Clean up
    os.remove(backend_dir / "create_db.py")
    
    print("✅ Backend setup complete!")

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🎨 Setting up Frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install Node.js dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    print("✅ Frontend setup complete!")

def create_sample_data():
    """Create some sample data for testing"""
    print("\n📊 Creating sample data...")
    
    sample_data_script = """
import sys
sys.path.append('.')
from models.database import SessionLocal
from models.schemas import Startup, Founder
from datetime import datetime

# Create sample startup
db = SessionLocal()

try:
    # Check if sample data already exists
    existing = db.query(Startup).filter(Startup.name == "TechCorp AI").first()
    if existing:
        print("Sample data already exists!")
        return
    
    sample_startup = Startup(
        name="TechCorp AI",
        sector="SaaS",
        stage="Seed",
        description="AI-powered business automation platform",
        website="https://techcorp-ai.com",
        location="San Francisco, CA",
        founded_year=2023,
        team_size=8,
        revenue=250000,
        arr=300000,
        burn_rate=50000,
        runway_months=18,
        funding_raised=1500000,
        valuation=10000000,
        cac=150,
        ltv=2400,
        churn_rate=0.03,
        growth_rate=0.12,
        created_at=datetime.utcnow()
    )
    
    db.add(sample_startup)
    db.flush()
    
    # Add sample founders
    founders = [
        Founder(
            startup_id=sample_startup.id,
            name="John Smith",
            role="CEO & Co-founder",
            email="john@techcorp-ai.com",
            linkedin="https://linkedin.com/in/johnsmith",
            background="Former VP of Engineering at Google",
            education="Stanford University - MS Computer Science",
            previous_experience="10 years at Google, 3 years at Meta",
            years_experience=13
        ),
        Founder(
            startup_id=sample_startup.id,
            name="Sarah Johnson",
            role="CTO & Co-founder",
            email="sarah@techcorp-ai.com",
            linkedin="https://linkedin.com/in/sarahjohnson",
            background="AI/ML expert with PhD in Computer Science",
            education="MIT - PhD Computer Science",
            previous_experience="5 years at OpenAI, 4 years at DeepMind",
            years_experience=9
        )
    ]
    
    for founder in founders:
        db.add(founder)
    
    db.commit()
    print("✅ Sample startup 'TechCorp AI' created successfully!")
    print(f"   Startup ID: {sample_startup.id}")
    print(f"   Founders: {len(founders)}")
    
except Exception as e:
    print(f"❌ Error creating sample data: {e}")
    db.rollback()
finally:
    db.close()
"""
    
    with open("backend/create_sample_data.py", "w") as f:
        f.write(sample_data_script)
    
    run_command("python create_sample_data.py", cwd="backend")
    
    # Clean up
    os.remove("backend/create_sample_data.py")

def main():
    """Main setup function"""
    print("🚀 Setting up AI Startup Evaluator for Local Development")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Error: Please run this script from the ai-startup-evaluator directory")
        print("   Expected structure:")
        print("   ai-startup-evaluator/")
        print("   ├── backend/")
        print("   ├── frontend/")
        print("   └── setup_local.py")
        sys.exit(1)
    
    # Setup backend
    setup_backend()
    
    # Setup frontend
    setup_frontend()
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Get a Google AI API key from https://aistudio.google.com/")
    print("2. Add it to backend/.env: GOOGLE_AI_API_KEY=your-key-here")
    print("3. Start the backend: cd backend && python -m uvicorn main:app --reload")
    print("4. Start the frontend: cd frontend && npm start")
    print("5. Open http://localhost:3000 in your browser")
    print("\n💡 Optional: Configure Google Cloud Storage for file uploads")
    print("   - Set up a GCS bucket and service account")
    print("   - Add credentials to backend/.env")
    print("\n🔍 Sample data created: 'TechCorp AI' startup for testing")

if __name__ == "__main__":
    main()
