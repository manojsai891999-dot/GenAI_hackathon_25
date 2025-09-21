from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Base models
class StartupBase(BaseModel):
    name: str
    sector: str
    stage: str
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    founded_year: Optional[int] = None
    team_size: Optional[int] = None
    revenue: Optional[float] = None
    arr: Optional[float] = None
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    funding_raised: Optional[float] = None
    valuation: Optional[float] = None
    cac: Optional[float] = None
    ltv: Optional[float] = None
    churn_rate: Optional[float] = None
    growth_rate: Optional[float] = None

class StartupCreate(StartupBase):
    pass

class StartupUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    stage: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    founded_year: Optional[int] = None
    team_size: Optional[int] = None
    revenue: Optional[float] = None
    arr: Optional[float] = None
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    funding_raised: Optional[float] = None
    valuation: Optional[float] = None
    cac: Optional[float] = None
    ltv: Optional[float] = None
    churn_rate: Optional[float] = None
    growth_rate: Optional[float] = None

class Startup(StartupBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Founder models
class FounderBase(BaseModel):
    name: str
    role: str
    email: Optional[str] = None
    linkedin: Optional[str] = None
    background: Optional[str] = None
    education: Optional[str] = None
    previous_experience: Optional[str] = None
    years_experience: Optional[int] = None

class FounderCreate(FounderBase):
    startup_id: int

class Founder(FounderBase):
    id: int
    startup_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Benchmark models
class BenchmarkBase(BaseModel):
    metric_name: str
    startup_value: Optional[float] = None
    benchmark_median: Optional[float] = None
    benchmark_p25: Optional[float] = None
    benchmark_p75: Optional[float] = None
    percentile_rank: Optional[float] = None
    comparison_result: Optional[str] = None

class BenchmarkCreate(BenchmarkBase):
    startup_id: int

class Benchmark(BenchmarkBase):
    id: int
    startup_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Risk models
class RiskBase(BaseModel):
    category: str
    risk_type: str
    description: str
    severity: str
    impact_score: Optional[float] = None
    likelihood_score: Optional[float] = None
    mitigation_suggestions: Optional[str] = None

class RiskCreate(RiskBase):
    startup_id: int

class Risk(RiskBase):
    id: int
    startup_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Interview models
class InterviewBase(BaseModel):
    interview_type: str
    transcript_summary: Optional[str] = None
    key_insights: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None
    red_flags: Optional[List[str]] = None
    positive_signals: Optional[List[str]] = None
    transcript_gcs_path: Optional[str] = None
    audio_gcs_path: Optional[str] = None
    interview_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None

class InterviewCreate(InterviewBase):
    startup_id: int

class Interview(InterviewBase):
    id: int
    startup_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Final Evaluation models
class FinalEvaluationBase(BaseModel):
    overall_score: float
    team_score: Optional[float] = None
    market_score: Optional[float] = None
    product_score: Optional[float] = None
    financial_score: Optional[float] = None
    traction_score: Optional[float] = None
    overall_flag: str
    team_flag: Optional[str] = None
    market_flag: Optional[str] = None
    product_flag: Optional[str] = None
    financial_flag: Optional[str] = None
    recommendation: str
    recommendation_reason: Optional[str] = None
    investment_amount_suggested: Optional[float] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    memo_gcs_path: Optional[str] = None
    evaluator_agent_version: Optional[str] = None

class FinalEvaluationCreate(FinalEvaluationBase):
    startup_id: int

class FinalEvaluation(FinalEvaluationBase):
    id: int
    startup_id: int
    evaluated_at: datetime
    
    class Config:
        from_attributes = True

# Complete startup response with all related data
class StartupComplete(Startup):
    founders: List[Founder] = []
    benchmarks: List[Benchmark] = []
    risks: List[Risk] = []
    interviews: List[Interview] = []
    final_evaluation: Optional[FinalEvaluation] = None

# Agent input/output models
class ExtractorAgentInput(BaseModel):
    file_path: str
    file_type: str  # pdf, pptx, form_data
    additional_data: Optional[Dict[str, Any]] = None

class ExtractorAgentOutput(BaseModel):
    startup_data: StartupCreate
    founders_data: List[FounderCreate]
    extraction_confidence: float
    extracted_fields: List[str]
    missing_fields: List[str]

class PublicDataExtractorInput(BaseModel):
    startup_id: int
    startup_data: Dict[str, Any]
    search_depth: str = "standard"  # light, standard, deep

class PublicDataExtractorOutput(BaseModel):
    benchmarks: List[BenchmarkCreate]
    public_data: Dict[str, Any]
    confidence_score: float
    data_sources: List[str]

class RiskAgentInput(BaseModel):
    startup_id: int
    startup_data: Dict[str, Any]
    benchmark_data: Dict[str, Any]
    public_data: Dict[str, Any]

class RiskAgentOutput(BaseModel):
    risks: List[RiskCreate]
    overall_risk_score: float
    risk_summary: str

class MemoAgentInput(BaseModel):
    startup_id: int
    all_data: Dict[str, Any]

class MemoAgentOutput(BaseModel):
    memo_content: str
    memo_gcs_path: str
    memo_format: str  # markdown, pdf

class VoiceInterviewAgentInput(BaseModel):
    startup_id: int
    audio_file_path: str
    interview_context: Optional[Dict[str, Any]] = None

class VoiceInterviewAgentOutput(BaseModel):
    interview_data: InterviewCreate
    processing_confidence: float

class FinalEvaluationAgentInput(BaseModel):
    startup_id: int
    all_agent_outputs: Dict[str, Any]

class FinalEvaluationAgentOutput(BaseModel):
    evaluation: FinalEvaluationCreate
    evaluation_confidence: float
    decision_factors: List[str]

class MeetingSchedulerAgentInput(BaseModel):
    startup_id: int
    startup_data: Dict[str, Any]
    memo_data: Dict[str, Any]
    evaluation_data: Dict[str, Any]

class MeetingSchedulerAgentOutput(BaseModel):
    meeting_scheduled: bool
    meeting_type: str
    priority: str
    scheduled_time: Optional[str] = None
    duration_minutes: int
    calendar_event_id: Optional[str] = None
    calendar_link: Optional[str] = None
    attendees: List[str]
    purpose: str
    alternative_slots: Optional[List[Dict[str, Any]]] = None
    materials_prepared: bool

class AudioInterviewAgentInput(BaseModel):
    startup_id: int
    meeting_details: Dict[str, Any]
    interview_type: str = "comprehensive"  # screening, deep_dive, comprehensive

class AudioInterviewAgentOutput(BaseModel):
    session_id: str
    interview_completed: bool
    overall_score: float
    total_questions: int
    avg_response_quality: float
    categories_covered: List[str]
    key_insights: List[str]
    red_flags: List[str]
    positive_signals: List[str]
    recommendation: str  # proceed, conditional, concerns
    next_steps: List[str]
    session_gcs_path: Optional[str] = None
    summary_gcs_path: Optional[str] = None

# API Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
