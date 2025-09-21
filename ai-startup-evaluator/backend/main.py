from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import tempfile
import logging
from typing import Optional, List

from models.database import get_db, create_tables
from models import schemas
from models.pydantic_models import (
    Startup, StartupCreate, StartupUpdate, StartupComplete,
    Founder, FounderCreate,
    Benchmark, BenchmarkCreate,
    Risk, RiskCreate,
    Interview, InterviewCreate,
    FinalEvaluation, FinalEvaluationCreate,
    APIResponse
)
# Temporarily commented out to fix import issues
# from agents.orchestrator import startup_evaluator
# from services.gcs_service import gcs_service

# Import the agent API
from api.agent_api import router as agent_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Startup Evaluator API",
    description="AI-powered startup evaluation platform with Google ADK agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",  # React dev server
        "https://ai-startup-evaluator-frontend-xxxxxxxxx-uc.a.run.app",  # Production frontend
        "https://*.run.app"  # Allow all Cloud Run services
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the agent API router
app.include_router(agent_router)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Database tables created successfully")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Startup Evaluator API is running"}

# Upload and process startup pitch deck - TEMPORARILY DISABLED
# @app.post("/api/upload", response_model=APIResponse)
# async def upload_pitch_deck(...):
#     # Commented out due to agent import issues
#     pass

# Get startup basic information
@app.get("/api/startup/{startup_id}", response_model=Startup)
async def get_startup(startup_id: int, db: Session = Depends(get_db)):
    """Get basic startup information"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup

# Get startup with all related data
@app.get("/api/startup/{startup_id}/complete", response_model=StartupComplete)
async def get_startup_complete(startup_id: int, db: Session = Depends(get_db)):
    """Get complete startup information with all related data"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # The SQLAlchemy relationships will automatically load related data
    return startup

# Get startup founders
@app.get("/api/startup/{startup_id}/founders", response_model=List[Founder])
async def get_startup_founders(startup_id: int, db: Session = Depends(get_db)):
    """Get founder information for a startup"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    founders = db.query(schemas.Founder).filter(schemas.Founder.startup_id == startup_id).all()
    return founders

# Get startup benchmarks
@app.get("/api/startup/{startup_id}/benchmarks", response_model=List[Benchmark])
async def get_startup_benchmarks(startup_id: int, db: Session = Depends(get_db)):
    """Get benchmark comparisons for a startup"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    benchmarks = db.query(schemas.Benchmark).filter(schemas.Benchmark.startup_id == startup_id).all()
    return benchmarks

# Get startup risks
@app.get("/api/startup/{startup_id}/risks", response_model=List[Risk])
async def get_startup_risks(startup_id: int, db: Session = Depends(get_db)):
    """Get risk assessment for a startup"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    risks = db.query(schemas.Risk).filter(schemas.Risk.startup_id == startup_id).all()
    return risks

# Get startup interview data
@app.get("/api/startup/{startup_id}/interview", response_model=List[Interview])
async def get_startup_interviews(startup_id: int, db: Session = Depends(get_db)):
    """Get interview analysis for a startup"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    interviews = db.query(schemas.Interview).filter(schemas.Interview.startup_id == startup_id).all()
    return interviews

# Get final evaluation
@app.get("/api/startup/{startup_id}/final", response_model=FinalEvaluation)
async def get_final_evaluation(startup_id: int, db: Session = Depends(get_db)):
    """Get final investment evaluation for a startup"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    evaluation = db.query(schemas.FinalEvaluation).filter(schemas.FinalEvaluation.startup_id == startup_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Final evaluation not found")
    
    return evaluation

# Get investment memo
@app.get("/api/startup/{startup_id}/memo")
async def get_investment_memo(startup_id: int, db: Session = Depends(get_db)):
    """Get investment memo for a startup"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    evaluation = db.query(schemas.FinalEvaluation).filter(schemas.FinalEvaluation.startup_id == startup_id).first()
    if not evaluation or not evaluation.memo_gcs_path:
        raise HTTPException(status_code=404, detail="Investment memo not found")
    
    # Temporarily disabled due to gcs_service import issues
    return APIResponse(
        success=False,
        message="Investment memo access temporarily disabled",
        data={"error": "GCS service not available"}
    )

# Get signed URLs for interview files
@app.get("/api/startup/{startup_id}/interview/{interview_id}/files")
async def get_interview_files(startup_id: int, interview_id: int, db: Session = Depends(get_db)):
    """Get signed URLs for interview transcript and audio files"""
    interview = db.query(schemas.Interview).filter(
        schemas.Interview.startup_id == startup_id,
        schemas.Interview.id == interview_id
    ).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Temporarily disabled due to gcs_service import issues
    return APIResponse(
        success=False,
        message="Interview file access temporarily disabled",
        data={"error": "GCS service not available"}
    )

# List all startups
@app.get("/api/startups", response_model=List[Startup])
async def list_startups(
    skip: int = 0,
    limit: int = 100,
    sector: Optional[str] = None,
    stage: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all startups with optional filtering"""
    query = db.query(schemas.Startup)
    
    if sector:
        query = query.filter(schemas.Startup.sector == sector)
    if stage:
        query = query.filter(schemas.Startup.stage == stage)
    
    startups = query.offset(skip).limit(limit).all()
    return startups

# Update startup information
@app.put("/api/startup/{startup_id}", response_model=Startup)
async def update_startup(
    startup_id: int,
    startup_update: StartupUpdate,
    db: Session = Depends(get_db)
):
    """Update startup information"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # Update only provided fields
    update_data = startup_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(startup, field, value)
    
    db.commit()
    db.refresh(startup)
    return startup

# Delete startup
@app.delete("/api/startup/{startup_id}")
async def delete_startup(startup_id: int, db: Session = Depends(get_db)):
    """Delete a startup and all related data"""
    startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # Delete related data (cascading should handle this, but explicit deletion for safety)
    db.query(schemas.Founder).filter(schemas.Founder.startup_id == startup_id).delete()
    db.query(schemas.Benchmark).filter(schemas.Benchmark.startup_id == startup_id).delete()
    db.query(schemas.Risk).filter(schemas.Risk.startup_id == startup_id).delete()
    db.query(schemas.Interview).filter(schemas.Interview.startup_id == startup_id).delete()
    db.query(schemas.FinalEvaluation).filter(schemas.FinalEvaluation.startup_id == startup_id).delete()
    
    # Delete startup
    db.delete(startup)
    db.commit()
    
    return APIResponse(
        success=True,
        message=f"Startup {startup_id} deleted successfully"
    )

# Get interview questions
@app.get("/api/interview/questions")
async def get_interview_questions(
    startup_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get predefined interview questions, optionally customized for a specific startup"""
    # Temporarily return basic interview questions without agent dependency
    basic_questions = {
        "Business Model": [
            "How does your startup make money?",
            "What is your pricing strategy?",
            "Who are your target customers?"
        ],
        "Market Opportunity": [
            "What problem are you solving?",
            "How big is your target market?",
            "Who are your main competitors?"
        ],
        "Team": [
            "What is your background?",
            "What makes your team uniquely qualified?",
            "Do you have any advisors?"
        ]
    }
    
    interview_script = []
    total_questions = 0
    for category, questions in basic_questions.items():
        interview_script.append({
            "category": category,
            "questions": questions,
            "estimated_time": f"{len(questions) * 2}-{len(questions) * 3} minutes"
        })
        total_questions += len(questions)
    
    return APIResponse(
        success=True,
        message="Basic interview questions retrieved successfully",
        data={
            "status": "success",
            "interview_script": interview_script,
            "total_categories": len(basic_questions),
            "total_questions": total_questions,
            "estimated_duration": f"{total_questions * 2}-{total_questions * 3} minutes"
        }
    )

# Get evaluation statistics
@app.get("/api/stats")
async def get_evaluation_stats(db: Session = Depends(get_db)):
    """Get overall evaluation statistics"""
    try:
        total_startups = db.query(schemas.Startup).count()
        total_evaluations = db.query(schemas.FinalEvaluation).count()
        
        # Count by recommendation
        pass_count = db.query(schemas.FinalEvaluation).filter(
            schemas.FinalEvaluation.recommendation == "pass"
        ).count()
        maybe_count = db.query(schemas.FinalEvaluation).filter(
            schemas.FinalEvaluation.recommendation == "maybe"
        ).count()
        reject_count = db.query(schemas.FinalEvaluation).filter(
            schemas.FinalEvaluation.recommendation == "reject"
        ).count()
        
        # Count by sector
        from sqlalchemy import func
        sector_stats = db.query(
            schemas.Startup.sector,
            func.count(schemas.Startup.id).label('count')
        ).group_by(schemas.Startup.sector).all()
        
        # Count by stage
        stage_stats = db.query(
            schemas.Startup.stage,
            func.count(schemas.Startup.id).label('count')
        ).group_by(schemas.Startup.stage).all()
        
        return APIResponse(
            success=True,
            message="Statistics retrieved successfully",
            data={
                "total_startups": total_startups,
                "total_evaluations": total_evaluations,
                "recommendations": {
                    "pass": pass_count,
                    "maybe": maybe_count,
                    "reject": reject_count
                },
                "by_sector": {stat.sector: stat.count for stat in sector_stats},
                "by_stage": {stat.stage: stat.count for stat in stage_stats}
            }
        )
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
