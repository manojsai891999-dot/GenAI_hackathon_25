from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Startup(Base):
    __tablename__ = "startups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    sector = Column(String(100), nullable=False)
    stage = Column(String(50), nullable=False)  # Pre-seed, Seed, Series A, etc.
    description = Column(Text)
    website = Column(String(255))
    location = Column(String(255))
    founded_year = Column(Integer)
    team_size = Column(Integer)
    
    # Financial metrics
    revenue = Column(Float)
    arr = Column(Float)  # Annual Recurring Revenue
    burn_rate = Column(Float)
    runway_months = Column(Integer)
    funding_raised = Column(Float)
    valuation = Column(Float)
    
    # Key metrics
    cac = Column(Float)  # Customer Acquisition Cost
    ltv = Column(Float)  # Lifetime Value
    churn_rate = Column(Float)
    growth_rate = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    founders = relationship("Founder", back_populates="startup")
    benchmarks = relationship("Benchmark", back_populates="startup")
    risks = relationship("Risk", back_populates="startup")
    interviews = relationship("Interview", back_populates="startup")
    final_evaluation = relationship("FinalEvaluation", back_populates="startup", uselist=False)

class Founder(Base):
    __tablename__ = "founders"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)  # CEO, CTO, etc.
    email = Column(String(255))
    linkedin = Column(String(255))
    background = Column(Text)
    education = Column(String(255))
    previous_experience = Column(Text)
    years_experience = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    startup = relationship("Startup", back_populates="founders")

class Benchmark(Base):
    __tablename__ = "benchmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)  # revenue, team_size, cac, etc.
    startup_value = Column(Float)
    benchmark_median = Column(Float)
    benchmark_p25 = Column(Float)
    benchmark_p75 = Column(Float)
    percentile_rank = Column(Float)  # Where startup ranks vs benchmark
    comparison_result = Column(String(20))  # above, below, average
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    startup = relationship("Startup", back_populates="benchmarks")

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    category = Column(String(50), nullable=False)  # financial, team, market, product, regulatory
    risk_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(10), nullable=False)  # green, yellow, red
    impact_score = Column(Float)  # 1-10 scale
    likelihood_score = Column(Float)  # 1-10 scale
    mitigation_suggestions = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    startup = relationship("Startup", back_populates="risks")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False)
    interview_type = Column(String(50), nullable=False)  # voice, video, text
    transcript_summary = Column(Text)
    key_insights = Column(JSON)  # Array of insights
    sentiment_score = Column(Float)  # -1 to 1
    confidence_score = Column(Float)  # 0 to 1
    red_flags = Column(JSON)  # Array of red flags
    positive_signals = Column(JSON)  # Array of positive signals
    
    # File references
    transcript_gcs_path = Column(String(500))
    audio_gcs_path = Column(String(500))
    
    # Metadata
    interview_date = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    startup = relationship("Startup", back_populates="interviews")

class FinalEvaluation(Base):
    __tablename__ = "final_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=False, unique=True)
    
    # Scores (1-10 scale)
    overall_score = Column(Float, nullable=False)
    team_score = Column(Float)
    market_score = Column(Float)
    product_score = Column(Float)
    financial_score = Column(Float)
    traction_score = Column(Float)
    
    # Flags
    overall_flag = Column(String(10), nullable=False)  # green, yellow, red
    team_flag = Column(String(10))
    market_flag = Column(String(10))
    product_flag = Column(String(10))
    financial_flag = Column(String(10))
    
    # Recommendation
    recommendation = Column(String(20), nullable=False)  # pass, maybe, reject
    recommendation_reason = Column(Text)
    investment_amount_suggested = Column(Float)
    
    # Summary
    strengths = Column(JSON)  # Array of strengths
    weaknesses = Column(JSON)  # Array of weaknesses
    next_steps = Column(JSON)  # Array of next steps
    
    # Memo reference
    memo_gcs_path = Column(String(500))
    
    # Metadata
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    evaluator_agent_version = Column(String(50))
    
    # Relationships
    startup = relationship("Startup", back_populates="final_evaluation")
