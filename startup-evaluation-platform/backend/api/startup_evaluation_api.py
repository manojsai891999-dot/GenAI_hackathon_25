"""
Startup Evaluation Platform - Main API Service
FastAPI-based backend service for coordinating AI agents and managing evaluations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio
from enum import Enum

# Google Cloud imports
from google.cloud import firestore
from google.cloud import storage
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel

app = FastAPI(
    title="Startup Evaluation Platform API",
    description="AI-powered startup evaluation and investment memo generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize Google Cloud clients
db = firestore.Client()
storage_client = storage.Client()
aiplatform.init(project="your-project-id", location="us-central1")

# Pydantic Models
class EvaluationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class StartupInfo(BaseModel):
    name: str = Field(..., description="Startup name")
    description: str = Field(..., description="Brief description of the startup")
    website: Optional[str] = Field(None, description="Company website")
    industry: str = Field(..., description="Industry/sector")
    stage: str = Field(..., description="Funding stage")
    location: str = Field(..., description="Company location")
    founded_year: int = Field(..., description="Year founded")

class FounderInfo(BaseModel):
    name: str = Field(..., description="Founder name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Phone number")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile")
    background: str = Field(..., description="Professional background")
    previous_companies: Optional[List[str]] = Field(None, description="Previous companies")

class EvaluationRequest(BaseModel):
    startup_info: StartupInfo
    founders: List[FounderInfo]
    documents: Optional[List[str]] = Field(None, description="Document URLs or IDs")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    priority: str = Field("medium", description="Evaluation priority: low, medium, high")

class EvaluationScores(BaseModel):
    founder_market_fit: float = Field(..., ge=0, le=100)
    problem_evaluation: float = Field(..., ge=0, le=100)
    usp_evaluation: float = Field(..., ge=0, le=100)
    team_profile: float = Field(..., ge=0, le=100)
    overall_score: float = Field(..., ge=0, le=100)

class EvaluationResponse(BaseModel):
    evaluation_id: str
    startup_id: str
    status: EvaluationStatus
    scores: Optional[EvaluationScores] = None
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None

class InterviewRequest(BaseModel):
    startup_id: str
    founder_email: str
    interview_type: str = Field("initial", description="Type of interview")
    preferred_times: List[datetime] = Field(..., description="Preferred meeting times")
    duration_minutes: int = Field(60, description="Interview duration in minutes")

class InterviewResponse(BaseModel):
    interview_id: str
    startup_id: str
    status: str
    scheduled_time: Optional[datetime] = None
    meeting_link: Optional[str] = None
    created_at: datetime

# Agent Service Classes
class EvaluationAgentService:
    """Service for interacting with the Evaluation Agent"""
    
    def __init__(self):
        self.model = GenerativeModel("gemini-1.5-pro")
    
    async def start_evaluation(self, evaluation_data: Dict[str, Any]) -> str:
        """Start evaluation process with the AI agent"""
        try:
            # Create evaluation record in Firestore
            evaluation_ref = db.collection('evaluations').document()
            evaluation_id = evaluation_ref.id
            
            evaluation_doc = {
                'startup_info': evaluation_data['startup_info'],
                'founders': evaluation_data['founders'],
                'status': EvaluationStatus.IN_PROGRESS,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'agent_status': 'initializing'
            }
            
            evaluation_ref.set(evaluation_doc)
            
            # Trigger agent workflow (async)
            asyncio.create_task(self._run_evaluation_workflow(evaluation_id, evaluation_data))
            
            return evaluation_id
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start evaluation: {str(e)}")
    
    async def _run_evaluation_workflow(self, evaluation_id: str, evaluation_data: Dict[str, Any]):
        """Run the complete evaluation workflow"""
        try:
            evaluation_ref = db.collection('evaluations').document(evaluation_id)
            
            # Step 1: Data extraction and preparation
            await self._update_status(evaluation_ref, "extracting_data")
            extracted_data = await self._extract_key_data(evaluation_data)
            
            # Step 2: Web research
            await self._update_status(evaluation_ref, "web_research")
            research_data = await self._conduct_web_research(extracted_data)
            
            # Step 3: Competitor analysis
            await self._update_status(evaluation_ref, "competitor_analysis")
            competitor_data = await self._analyze_competitors(extracted_data, research_data)
            
            # Step 4: Market research
            await self._update_status(evaluation_ref, "market_research")
            market_data = await self._research_market(extracted_data)
            
            # Step 5: Founder analysis
            await self._update_status(evaluation_ref, "founder_analysis")
            founder_analysis = await self._analyze_founders(evaluation_data['founders'])
            
            # Step 6: Team evaluation
            await self._update_status(evaluation_ref, "team_evaluation")
            team_analysis = await self._evaluate_team(evaluation_data)
            
            # Step 7: Calculate scores
            await self._update_status(evaluation_ref, "calculating_scores")
            scores = await self._calculate_scores(
                extracted_data, research_data, competitor_data, 
                market_data, founder_analysis, team_analysis
            )
            
            # Step 8: Generate report
            await self._update_status(evaluation_ref, "generating_report")
            report = await self._generate_report(scores, {
                'research': research_data,
                'competitors': competitor_data,
                'market': market_data,
                'founders': founder_analysis,
                'team': team_analysis
            })
            
            # Final update
            evaluation_ref.update({
                'status': EvaluationStatus.COMPLETED,
                'scores': scores,
                'report': report,
                'updated_at': datetime.utcnow(),
                'completed_at': datetime.utcnow()
            })
            
        except Exception as e:
            evaluation_ref.update({
                'status': EvaluationStatus.FAILED,
                'error': str(e),
                'updated_at': datetime.utcnow()
            })
    
    async def _update_status(self, evaluation_ref, status: str):
        """Update evaluation status"""
        evaluation_ref.update({
            'agent_status': status,
            'updated_at': datetime.utcnow()
        })
    
    async def _extract_key_data(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure key data from input"""
        # Implementation for data extraction
        return {"extracted": True}
    
    async def _conduct_web_research(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct web research using Vertex AI Search"""
        # Implementation for web research
        return {"research_completed": True}
    
    async def _analyze_competitors(self, extracted_data: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        # Implementation for competitor analysis
        return {"competitors_analyzed": True}
    
    async def _research_market(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research market size and trends"""
        # Implementation for market research
        return {"market_researched": True}
    
    async def _analyze_founders(self, founders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze founder backgrounds and fit"""
        # Implementation for founder analysis
        return {"founders_analyzed": True}
    
    async def _evaluate_team(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate team composition and capabilities"""
        # Implementation for team evaluation
        return {"team_evaluated": True}
    
    async def _calculate_scores(self, *args) -> Dict[str, float]:
        """Calculate evaluation scores based on all analysis"""
        # Implementation for score calculation
        return {
            "founder_market_fit": 75.0,
            "problem_evaluation": 80.0,
            "usp_evaluation": 70.0,
            "team_profile": 85.0,
            "overall_score": 77.5
        }
    
    async def _generate_report(self, scores: Dict[str, float], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        # Implementation for report generation
        return {
            "summary": "Comprehensive evaluation completed",
            "recommendations": ["Strong team", "Market validation needed"],
            "risk_factors": ["Competition", "Market timing"]
        }

class SchedulingAgentService:
    """Service for interacting with the Scheduling Agent"""
    
    async def schedule_interview(self, interview_request: InterviewRequest) -> str:
        """Schedule interview with founder"""
        try:
            interview_ref = db.collection('interviews').document()
            interview_id = interview_ref.id
            
            interview_doc = {
                'startup_id': interview_request.startup_id,
                'founder_email': interview_request.founder_email,
                'interview_type': interview_request.interview_type,
                'preferred_times': [t.isoformat() for t in interview_request.preferred_times],
                'duration_minutes': interview_request.duration_minutes,
                'status': 'scheduling',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            interview_ref.set(interview_doc)
            
            # Trigger scheduling workflow
            asyncio.create_task(self._run_scheduling_workflow(interview_id, interview_request))
            
            return interview_id
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to schedule interview: {str(e)}")
    
    async def _run_scheduling_workflow(self, interview_id: str, interview_request: InterviewRequest):
        """Run the scheduling workflow"""
        # Implementation for scheduling workflow
        pass

class InterviewAgentService:
    """Service for interacting with the Interview Agent"""
    
    async def conduct_interview(self, interview_id: str) -> Dict[str, Any]:
        """Conduct AI-powered interview"""
        # Implementation for interview conduction
        return {"interview_completed": True}

# Initialize services
evaluation_service = EvaluationAgentService()
scheduling_service = SchedulingAgentService()
interview_service = InterviewAgentService()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user info"""
    # Implementation for token validation
    return {"user_id": "test_user", "email": "test@example.com"}

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Startup Evaluation Platform API", "status": "healthy"}

@app.post("/evaluations", response_model=EvaluationResponse)
async def create_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Start a new startup evaluation"""
    try:
        # Generate startup ID
        startup_id = str(uuid.uuid4())
        
        # Prepare evaluation data
        evaluation_data = {
            'startup_id': startup_id,
            'startup_info': request.startup_info.dict(),
            'founders': [f.dict() for f in request.founders],
            'documents': request.documents or [],
            'additional_info': request.additional_info or {},
            'priority': request.priority,
            'user_id': current_user['user_id']
        }
        
        # Start evaluation
        evaluation_id = await evaluation_service.start_evaluation(evaluation_data)
        
        return EvaluationResponse(
            evaluation_id=evaluation_id,
            startup_id=startup_id,
            status=EvaluationStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            estimated_completion=datetime.utcnow().replace(hour=datetime.utcnow().hour + 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get evaluation status and results"""
    try:
        evaluation_ref = db.collection('evaluations').document(evaluation_id)
        evaluation_doc = evaluation_ref.get()
        
        if not evaluation_doc.exists:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        data = evaluation_doc.to_dict()
        
        return EvaluationResponse(
            evaluation_id=evaluation_id,
            startup_id=data.get('startup_id', ''),
            status=EvaluationStatus(data.get('status', 'pending')),
            scores=EvaluationScores(**data['scores']) if data.get('scores') else None,
            summary=data.get('report', {}).get('summary'),
            recommendations=data.get('report', {}).get('recommendations'),
            risk_factors=data.get('report', {}).get('risk_factors'),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluations")
async def list_evaluations(
    status: Optional[EvaluationStatus] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """List evaluations for the current user"""
    try:
        query = db.collection('evaluations').where('user_id', '==', current_user['user_id'])
        
        if status:
            query = query.where('status', '==', status.value)
        
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        
        evaluations = []
        for doc in query.stream():
            data = doc.to_dict()
            evaluations.append({
                'evaluation_id': doc.id,
                'startup_name': data.get('startup_info', {}).get('name'),
                'status': data.get('status'),
                'created_at': data.get('created_at'),
                'overall_score': data.get('scores', {}).get('overall_score')
            })
        
        return {"evaluations": evaluations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interviews", response_model=InterviewResponse)
async def schedule_interview(
    request: InterviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """Schedule an interview with a startup founder"""
    try:
        interview_id = await scheduling_service.schedule_interview(request)
        
        return InterviewResponse(
            interview_id=interview_id,
            startup_id=request.startup_id,
            status="scheduling",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interviews/{interview_id}")
async def get_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get interview details and status"""
    try:
        interview_ref = db.collection('interviews').document(interview_id)
        interview_doc = interview_ref.get()
        
        if not interview_doc.exists:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return interview_doc.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interviews/{interview_id}/conduct")
async def conduct_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start conducting the interview with AI agent"""
    try:
        result = await interview_service.conduct_interview(interview_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/investment-memo/{startup_id}")
async def generate_investment_memo(
    startup_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate investment memo for a startup"""
    try:
        # Get evaluation data
        evaluations_query = db.collection('evaluations').where('startup_id', '==', startup_id)
        evaluations = list(evaluations_query.stream())
        
        if not evaluations:
            raise HTTPException(status_code=404, detail="No evaluation found for this startup")
        
        # Get interview data
        interviews_query = db.collection('interviews').where('startup_id', '==', startup_id)
        interviews = list(interviews_query.stream())
        
        # Generate memo using AI
        memo_data = {
            'startup_id': startup_id,
            'evaluation_data': [doc.to_dict() for doc in evaluations],
            'interview_data': [doc.to_dict() for doc in interviews],
            'generated_at': datetime.utcnow()
        }
        
        # Store memo
        memo_ref = db.collection('investment_memos').document()
        memo_ref.set(memo_data)
        
        return {"memo_id": memo_ref.id, "memo_data": memo_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
