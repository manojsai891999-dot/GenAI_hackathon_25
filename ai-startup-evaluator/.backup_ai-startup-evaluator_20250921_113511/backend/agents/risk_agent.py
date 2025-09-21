import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents import Agent

from ..models.pydantic_models import (
    RiskAgentInput,
    RiskAgentOutput,
    RiskCreate
)

logger = logging.getLogger(__name__)

def analyze_financial_risks(startup_data: dict, benchmark_data: dict) -> dict:
    """Analyze financial risks based on startup metrics and benchmarks"""
    try:
        risks = []
        
        # Check burn rate vs runway
        burn_rate = startup_data.get("burn_rate")
        runway_months = startup_data.get("runway_months")
        
        if burn_rate and runway_months:
            if runway_months < 6:
                risks.append({
                    "category": "financial",
                    "risk_type": "short_runway",
                    "description": f"Company has only {runway_months} months of runway remaining",
                    "severity": "red",
                    "impact_score": 9.0,
                    "likelihood_score": 8.0,
                    "mitigation_suggestions": "Immediate fundraising required or significant cost reduction"
                })
            elif runway_months < 12:
                risks.append({
                    "category": "financial",
                    "risk_type": "moderate_runway",
                    "description": f"Company has {runway_months} months of runway, should start fundraising soon",
                    "severity": "yellow",
                    "impact_score": 6.0,
                    "likelihood_score": 5.0,
                    "mitigation_suggestions": "Begin fundraising process within next 3 months"
                })
        
        # Check revenue growth
        growth_rate = startup_data.get("growth_rate")
        if growth_rate is not None:
            if growth_rate < 0.05:  # Less than 5% monthly growth
                risks.append({
                    "category": "financial",
                    "risk_type": "low_growth",
                    "description": f"Monthly growth rate of {growth_rate*100:.1f}% is below healthy startup levels",
                    "severity": "yellow",
                    "impact_score": 7.0,
                    "likelihood_score": 6.0,
                    "mitigation_suggestions": "Focus on product-market fit and customer acquisition strategies"
                })
        
        # Check CAC vs LTV ratio
        cac = startup_data.get("cac")
        ltv = startup_data.get("ltv")
        if cac and ltv and cac > 0:
            ltv_cac_ratio = ltv / cac
            if ltv_cac_ratio < 3:
                risks.append({
                    "category": "financial",
                    "risk_type": "poor_unit_economics",
                    "description": f"LTV/CAC ratio of {ltv_cac_ratio:.1f} is below the healthy 3:1 threshold",
                    "severity": "red" if ltv_cac_ratio < 2 else "yellow",
                    "impact_score": 8.0,
                    "likelihood_score": 7.0,
                    "mitigation_suggestions": "Optimize customer acquisition costs or improve customer lifetime value"
                })
        
        return {"status": "success", "risks": risks}
    except Exception as e:
        logger.error(f"Financial risk analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def analyze_team_risks(startup_data: dict, founders_data: list) -> dict:
    """Analyze team-related risks"""
    try:
        risks = []
        
        # Check team size
        team_size = startup_data.get("team_size", 0)
        stage = startup_data.get("stage", "").lower()
        
        if stage in ["seed", "series a"] and team_size < 5:
            risks.append({
                "category": "team",
                "risk_type": "small_team",
                "description": f"Team size of {team_size} may be insufficient for {stage} stage",
                "severity": "yellow",
                "impact_score": 5.0,
                "likelihood_score": 4.0,
                "mitigation_suggestions": "Consider strategic hires in key areas"
            })
        
        # Check founder experience
        if not founders_data:
            risks.append({
                "category": "team",
                "risk_type": "no_founder_info",
                "description": "No founder information available for assessment",
                "severity": "yellow",
                "impact_score": 6.0,
                "likelihood_score": 5.0,
                "mitigation_suggestions": "Provide detailed founder backgrounds and experience"
            })
        else:
            total_experience = sum(f.get("years_experience", 0) for f in founders_data if f.get("years_experience"))
            avg_experience = total_experience / len(founders_data) if founders_data else 0
            
            if avg_experience < 5:
                risks.append({
                    "category": "team",
                    "risk_type": "inexperienced_founders",
                    "description": f"Founders have average {avg_experience:.1f} years experience",
                    "severity": "yellow",
                    "impact_score": 6.0,
                    "likelihood_score": 5.0,
                    "mitigation_suggestions": "Consider adding experienced advisors or senior hires"
                })
        
        return {"status": "success", "risks": risks}
    except Exception as e:
        logger.error(f"Team risk analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def analyze_market_risks(startup_data: dict, public_data: dict) -> dict:
    """Analyze market and competitive risks"""
    try:
        risks = []
        sector = startup_data.get("sector", "")
        
        # Sector-specific risks
        high_competition_sectors = ["E-commerce", "SaaS", "FinTech"]
        if sector in high_competition_sectors:
            risks.append({
                "category": "market",
                "risk_type": "high_competition",
                "description": f"{sector} is a highly competitive market with many established players",
                "severity": "yellow",
                "impact_score": 6.0,
                "likelihood_score": 7.0,
                "mitigation_suggestions": "Focus on unique value proposition and defensible moats"
            })
        
        # Check market presence from public data
        company_info = public_data.get("company", {})
        market_presence = company_info.get("market_presence", 0.5)
        
        if market_presence < 0.3:
            risks.append({
                "category": "market",
                "risk_type": "low_market_presence",
                "description": "Limited online presence and market visibility",
                "severity": "yellow",
                "impact_score": 5.0,
                "likelihood_score": 6.0,
                "mitigation_suggestions": "Increase marketing efforts and thought leadership"
            })
        
        return {"status": "success", "risks": risks}
    except Exception as e:
        logger.error(f"Market risk analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def analyze_product_risks(startup_data: dict) -> dict:
    """Analyze product-related risks"""
    try:
        risks = []
        
        # Check if product metrics are available
        revenue = startup_data.get("revenue")
        arr = startup_data.get("arr")
        
        if not revenue and not arr:
            risks.append({
                "category": "product",
                "risk_type": "no_revenue",
                "description": "No revenue metrics available, indicating early-stage product",
                "severity": "yellow",
                "impact_score": 7.0,
                "likelihood_score": 6.0,
                "mitigation_suggestions": "Focus on achieving product-market fit and initial revenue"
            })
        
        # Check churn rate
        churn_rate = startup_data.get("churn_rate")
        if churn_rate and churn_rate > 0.1:  # More than 10% monthly churn
            risks.append({
                "category": "product",
                "risk_type": "high_churn",
                "description": f"Monthly churn rate of {churn_rate*100:.1f}% indicates product-market fit issues",
                "severity": "red",
                "impact_score": 8.0,
                "likelihood_score": 7.0,
                "mitigation_suggestions": "Investigate customer satisfaction and product stickiness"
            })
        
        return {"status": "success", "risks": risks}
    except Exception as e:
        logger.error(f"Product risk analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def analyze_regulatory_risks(startup_data: dict) -> dict:
    """Analyze regulatory and compliance risks"""
    try:
        risks = []
        sector = startup_data.get("sector", "").lower()
        
        # High-regulation sectors
        if "fintech" in sector or "finance" in sector:
            risks.append({
                "category": "regulatory",
                "risk_type": "financial_regulations",
                "description": "FinTech companies face complex regulatory requirements",
                "severity": "yellow",
                "impact_score": 7.0,
                "likelihood_score": 8.0,
                "mitigation_suggestions": "Ensure compliance with financial regulations and obtain necessary licenses"
            })
        
        if "health" in sector or "medical" in sector:
            risks.append({
                "category": "regulatory",
                "risk_type": "healthcare_regulations",
                "description": "Healthcare companies must comply with HIPAA, FDA, and other regulations",
                "severity": "yellow",
                "impact_score": 8.0,
                "likelihood_score": 7.0,
                "mitigation_suggestions": "Implement robust compliance framework and regulatory strategy"
            })
        
        return {"status": "success", "risks": risks}
    except Exception as e:
        logger.error(f"Regulatory risk analysis failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_overall_risk_score(all_risks: list) -> dict:
    """Calculate overall risk score and summary"""
    try:
        if not all_risks:
            return {
                "status": "success",
                "overall_risk_score": 3.0,
                "risk_summary": "No significant risks identified"
            }
        
        # Calculate weighted risk score
        total_weighted_score = 0
        total_weight = 0
        
        red_risks = [r for r in all_risks if r.get("severity") == "red"]
        yellow_risks = [r for r in all_risks if r.get("severity") == "yellow"]
        green_risks = [r for r in all_risks if r.get("severity") == "green"]
        
        # Weight: red=3, yellow=2, green=1
        for risk in red_risks:
            impact = risk.get("impact_score", 5.0)
            likelihood = risk.get("likelihood_score", 5.0)
            risk_score = (impact + likelihood) / 2
            total_weighted_score += risk_score * 3
            total_weight += 3
        
        for risk in yellow_risks:
            impact = risk.get("impact_score", 5.0)
            likelihood = risk.get("likelihood_score", 5.0)
            risk_score = (impact + likelihood) / 2
            total_weighted_score += risk_score * 2
            total_weight += 2
        
        for risk in green_risks:
            impact = risk.get("impact_score", 5.0)
            likelihood = risk.get("likelihood_score", 5.0)
            risk_score = (impact + likelihood) / 2
            total_weighted_score += risk_score * 1
            total_weight += 1
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 3.0
        
        # Generate summary
        risk_summary = f"Identified {len(all_risks)} risks: {len(red_risks)} high, {len(yellow_risks)} medium, {len(green_risks)} low severity"
        
        return {
            "status": "success",
            "overall_risk_score": round(overall_score, 2),
            "risk_summary": risk_summary
        }
    except Exception as e:
        logger.error(f"Risk score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the RiskAgent using Google ADK
risk_agent = Agent(
    name="startup_risk_agent",
    model="gemini-2.0-flash",
    description="Agent specialized in identifying and analyzing investment risks for startups",
    instruction="""
    You are an expert investment risk analyst agent. Your role is to identify and analyze various types of risks associated with startup investments.
    
    Analyze the following risk categories:
    
    1. FINANCIAL RISKS:
       - Burn rate and runway analysis
       - Revenue growth patterns
       - Unit economics (CAC/LTV ratios)
       - Funding requirements
    
    2. TEAM RISKS:
       - Founder experience and background
       - Team size and composition
       - Key person dependencies
    
    3. MARKET RISKS:
       - Competitive landscape
       - Market size and growth
       - Market presence and visibility
    
    4. PRODUCT RISKS:
       - Product-market fit indicators
       - Customer churn and retention
       - Technical feasibility
    
    5. REGULATORY RISKS:
       - Compliance requirements
       - Regulatory changes
       - Legal challenges
    
    For each risk identified, provide:
    - Category (financial, team, market, product, regulatory)
    - Risk type (specific risk identifier)
    - Description (clear explanation of the risk)
    - Severity (green, yellow, red)
    - Impact score (1-10 scale)
    - Likelihood score (1-10 scale)
    - Mitigation suggestions
    
    Use the available tools to analyze different risk categories and calculate overall risk scores.
    """,
    tools=[
        analyze_financial_risks,
        analyze_team_risks,
        analyze_market_risks,
        analyze_product_risks,
        analyze_regulatory_risks,
        calculate_overall_risk_score
    ]
)
