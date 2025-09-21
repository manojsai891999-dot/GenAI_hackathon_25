#!/usr/bin/env python3
"""
Create sample data for the AI Startup Evaluator
"""
import sys
import os
sys.path.append('.')

from models.database import get_db, create_tables
from models import schemas
from sqlalchemy.orm import Session
from datetime import datetime

def create_sample_data():
    """Create sample startup data for testing"""
    
    # Create database tables if they don't exist
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if sample data already exists
        existing_startup = db.query(schemas.Startup).filter(schemas.Startup.name == "TechCorp AI").first()
        if existing_startup:
            print("Sample data already exists!")
            return
        
        # Create sample startup
        startup = schemas.Startup(
            name="TechCorp AI",
            sector="SaaS",
            stage="Seed",
            description="AI-powered customer service automation platform",
            website="https://techcorp-ai.com",
            founded_year=2023,
            location="San Francisco, CA",
            funding_raised=2500000,
            team_size=12
        )
        db.add(startup)
        db.flush()  # Get the ID
        
        # Create sample founders
        founder1 = schemas.Founder(
            startup_id=startup.id,
            name="John Smith",
            role="CEO",
            background="Former VP of Engineering at Salesforce, 10+ years in AI/ML",
            linkedin="https://linkedin.com/in/johnsmith",
            education="Stanford University - MS Computer Science"
        )
        
        founder2 = schemas.Founder(
            startup_id=startup.id,
            name="Sarah Johnson",
            role="CTO",
            background="Ex-Google AI researcher, PhD in Machine Learning",
            linkedin="https://linkedin.com/in/sarahjohnson",
            education="MIT - PhD Machine Learning"
        )
        
        db.add(founder1)
        db.add(founder2)
        
        # Create sample benchmarks
        benchmark1 = schemas.Benchmark(
            startup_id=startup.id,
            metric_name="Customer Acquisition Cost",
            startup_value=150.0,
            benchmark_median=200.0,
            percentile_rank=75.0,
            comparison_result="above"
        )
        
        benchmark2 = schemas.Benchmark(
            startup_id=startup.id,
            metric_name="Monthly Recurring Revenue Growth",
            startup_value=25.0,
            benchmark_median=15.0,
            percentile_rank=85.0,
            comparison_result="above"
        )
        
        db.add(benchmark1)
        db.add(benchmark2)
        
        # Create sample risks
        risk1 = schemas.Risk(
            startup_id=startup.id,
            category="market",
            risk_type="Competition Risk",
            description="High competition from established players like Zendesk and Intercom",
            severity="yellow",
            impact_score=6.0,
            likelihood_score=8.0,
            mitigation_suggestions="Focus on AI differentiation and superior automation capabilities"
        )
        
        risk2 = schemas.Risk(
            startup_id=startup.id,
            category="technical",
            risk_type="Dependency Risk",
            description="Dependency on third-party AI models and APIs",
            severity="green",
            impact_score=4.0,
            likelihood_score=5.0,
            mitigation_suggestions="Develop proprietary models and maintain multiple AI provider relationships"
        )
        
        db.add(risk1)
        db.add(risk2)
        
        # Create sample interview
        interview = schemas.Interview(
            startup_id=startup.id,
            interview_type="voice",
            duration_minutes=45,
            sentiment_score=0.75,
            confidence_score=0.85,
            transcript_summary="Comprehensive discussion covering business model, market opportunity, and technical approach"
        )
        
        db.add(interview)
        
        # Create sample final evaluation
        final_eval = schemas.FinalEvaluation(
            startup_id=startup.id,
            overall_score=7.8,
            overall_flag="green",
            recommendation="pass",
            recommendation_reason="Strong technical team with innovative AI approach in growing market",
            investment_amount_suggested=1000000
        )
        
        db.add(final_eval)
        
        # Create another sample startup
        startup2 = schemas.Startup(
            name="GreenTech Solutions",
            sector="CleanTech",
            stage="Series A",
            description="Solar energy optimization using IoT and machine learning",
            website="https://greentech-solutions.com",
            founded_year=2022,
            location="Austin, TX",
            funding_raised=5000000,
            team_size=25
        )
        db.add(startup2)
        db.flush()
        
        # Final evaluation for second startup
        final_eval2 = schemas.FinalEvaluation(
            startup_id=startup2.id,
            overall_score=6.5,
            overall_flag="yellow",
            recommendation="maybe",
            recommendation_reason="Experienced team and proven technology, but high capital requirements and regulatory challenges",
            investment_amount_suggested=750000
        )
        
        db.add(final_eval2)
        
        # Commit all changes
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"   - Created startup: {startup.name}")
        print(f"   - Created startup: {startup2.name}")
        print(f"   - Added 2 founders, 2 benchmarks, 2 risks, 1 interview, 2 evaluations")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
