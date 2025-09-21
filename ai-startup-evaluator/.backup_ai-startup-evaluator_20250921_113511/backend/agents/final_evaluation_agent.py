import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents import Agent

from ..models.pydantic_models import (
    FinalEvaluationAgentInput,
    FinalEvaluationAgentOutput,
    FinalEvaluationCreate
)

logger = logging.getLogger(__name__)

def calculate_team_score(startup_data: dict, founders_data: list, public_data: dict) -> dict:
    """Calculate team evaluation score (1-10)"""
    try:
        score = 5.0  # Base score
        factors = []
        
        # Founder experience
        if founders_data:
            total_experience = sum(f.get("years_experience", 0) for f in founders_data if f.get("years_experience"))
            avg_experience = total_experience / len(founders_data) if founders_data else 0
            
            if avg_experience >= 10:
                score += 2.0
                factors.append("Strong founder experience (10+ years avg)")
            elif avg_experience >= 5:
                score += 1.0
                factors.append("Good founder experience (5+ years avg)")
            elif avg_experience < 3:
                score -= 1.0
                factors.append("Limited founder experience")
        else:
            score -= 1.5
            factors.append("No founder information available")
        
        # Team size appropriateness
        team_size = startup_data.get("team_size", 0)
        stage = startup_data.get("stage", "").lower()
        
        if stage in ["seed", "series a"]:
            if 5 <= team_size <= 20:
                score += 1.0
                factors.append("Appropriate team size for stage")
            elif team_size < 5:
                score -= 0.5
                factors.append("Small team for current stage")
            elif team_size > 30:
                score -= 1.0
                factors.append("Large team may indicate high burn")
        
        # Public credibility from founder info
        founder_credibility = public_data.get("founders", {})
        if founder_credibility:
            avg_credibility = sum(f.get("credibility_score", 0.5) for f in founder_credibility.values()) / len(founder_credibility)
            if avg_credibility > 0.7:
                score += 1.0
                factors.append("Strong online presence and credibility")
            elif avg_credibility < 0.3:
                score -= 0.5
                factors.append("Limited online presence")
        
        # Ensure score is within bounds
        final_score = max(1.0, min(10.0, score))
        
        return {
            "status": "success",
            "score": round(final_score, 1),
            "factors": factors
        }
    except Exception as e:
        logger.error(f"Team score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_market_score(startup_data: dict, benchmark_data: list, public_data: dict) -> dict:
    """Calculate market evaluation score (1-10)"""
    try:
        score = 5.0  # Base score
        factors = []
        
        # Market presence
        company_info = public_data.get("company", {})
        market_presence = company_info.get("market_presence", 0.5)
        
        if market_presence > 0.7:
            score += 1.5
            factors.append("Strong market presence and visibility")
        elif market_presence > 0.4:
            score += 0.5
            factors.append("Moderate market presence")
        else:
            score -= 0.5
            factors.append("Limited market visibility")
        
        # Sector competitiveness
        sector = startup_data.get("sector", "")
        high_competition_sectors = ["SaaS", "E-commerce", "FinTech"]
        
        if sector in high_competition_sectors:
            score -= 0.5
            factors.append(f"Highly competitive {sector} market")
        else:
            score += 0.5
            factors.append(f"Favorable market conditions in {sector}")
        
        # Benchmark performance
        above_benchmark_count = sum(1 for b in benchmark_data if b.get("comparison_result") == "above")
        below_benchmark_count = sum(1 for b in benchmark_data if b.get("comparison_result") == "below")
        
        if above_benchmark_count > below_benchmark_count:
            score += 1.0
            factors.append("Performing above industry benchmarks")
        elif below_benchmark_count > above_benchmark_count:
            score -= 1.0
            factors.append("Performing below industry benchmarks")
        
        # Growth stage appropriateness
        stage = startup_data.get("stage", "").lower()
        revenue = startup_data.get("revenue", 0)
        
        if stage == "series a" and revenue > 1000000:  # $1M+ revenue
            score += 1.0
            factors.append("Strong revenue for Series A stage")
        elif stage == "seed" and revenue > 100000:  # $100K+ revenue
            score += 0.5
            factors.append("Good early revenue traction")
        
        # Ensure score is within bounds
        final_score = max(1.0, min(10.0, score))
        
        return {
            "status": "success",
            "score": round(final_score, 1),
            "factors": factors
        }
    except Exception as e:
        logger.error(f"Market score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_product_score(startup_data: dict, interview_data: dict) -> dict:
    """Calculate product evaluation score (1-10)"""
    try:
        score = 5.0  # Base score
        factors = []
        
        # Revenue indicators
        revenue = startup_data.get("revenue", 0)
        arr = startup_data.get("arr", 0)
        
        if arr > 1000000:  # $1M+ ARR
            score += 2.0
            factors.append("Strong recurring revenue ($1M+ ARR)")
        elif arr > 100000:  # $100K+ ARR
            score += 1.0
            factors.append("Good recurring revenue traction")
        elif revenue > 500000:  # $500K+ revenue
            score += 1.0
            factors.append("Solid revenue generation")
        elif revenue > 0:
            score += 0.5
            factors.append("Early revenue traction")
        else:
            score -= 1.0
            factors.append("No revenue yet")
        
        # Customer retention (churn rate)
        churn_rate = startup_data.get("churn_rate")
        if churn_rate is not None:
            if churn_rate < 0.05:  # Less than 5% monthly churn
                score += 1.5
                factors.append("Excellent customer retention (low churn)")
            elif churn_rate < 0.1:  # Less than 10% monthly churn
                score += 0.5
                factors.append("Good customer retention")
            else:
                score -= 1.5
                factors.append("High customer churn indicates product issues")
        
        # Growth rate
        growth_rate = startup_data.get("growth_rate")
        if growth_rate is not None:
            if growth_rate > 0.15:  # 15%+ monthly growth
                score += 1.5
                factors.append("Excellent growth rate (15%+ monthly)")
            elif growth_rate > 0.08:  # 8%+ monthly growth
                score += 1.0
                factors.append("Strong growth rate")
            elif growth_rate > 0.03:  # 3%+ monthly growth
                score += 0.5
                factors.append("Moderate growth rate")
            else:
                score -= 1.0
                factors.append("Low or negative growth")
        
        # Interview insights about product
        if interview_data:
            positive_signals = interview_data.get("positive_signals", [])
            product_mentions = [s for s in positive_signals if "product" in s.lower() or "traction" in s.lower()]
            if product_mentions:
                score += 0.5
                factors.append("Positive product feedback in interview")
        
        # Ensure score is within bounds
        final_score = max(1.0, min(10.0, score))
        
        return {
            "status": "success",
            "score": round(final_score, 1),
            "factors": factors
        }
    except Exception as e:
        logger.error(f"Product score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_financial_score(startup_data: dict, risks_data: list) -> dict:
    """Calculate financial evaluation score (1-10)"""
    try:
        score = 5.0  # Base score
        factors = []
        
        # Unit economics (CAC/LTV)
        cac = startup_data.get("cac")
        ltv = startup_data.get("ltv")
        
        if cac and ltv and cac > 0:
            ltv_cac_ratio = ltv / cac
            if ltv_cac_ratio >= 5:
                score += 2.0
                factors.append(f"Excellent unit economics (LTV/CAC: {ltv_cac_ratio:.1f}x)")
            elif ltv_cac_ratio >= 3:
                score += 1.0
                factors.append(f"Good unit economics (LTV/CAC: {ltv_cac_ratio:.1f}x)")
            elif ltv_cac_ratio >= 2:
                score += 0.5
                factors.append(f"Acceptable unit economics (LTV/CAC: {ltv_cac_ratio:.1f}x)")
            else:
                score -= 2.0
                factors.append(f"Poor unit economics (LTV/CAC: {ltv_cac_ratio:.1f}x)")
        
        # Runway analysis
        runway_months = startup_data.get("runway_months")
        if runway_months is not None:
            if runway_months >= 18:
                score += 1.0
                factors.append(f"Strong runway ({runway_months} months)")
            elif runway_months >= 12:
                score += 0.5
                factors.append(f"Adequate runway ({runway_months} months)")
            elif runway_months >= 6:
                score -= 0.5
                factors.append(f"Limited runway ({runway_months} months)")
            else:
                score -= 2.0
                factors.append(f"Critical runway shortage ({runway_months} months)")
        
        # Financial risks impact
        financial_risks = [r for r in risks_data if r.get("category") == "financial"]
        red_financial_risks = [r for r in financial_risks if r.get("severity") == "red"]
        
        if red_financial_risks:
            score -= len(red_financial_risks) * 1.0
            factors.append(f"{len(red_financial_risks)} critical financial risks identified")
        
        # Revenue growth consistency
        growth_rate = startup_data.get("growth_rate")
        revenue = startup_data.get("revenue", 0)
        
        if growth_rate and growth_rate > 0 and revenue > 0:
            score += 0.5
            factors.append("Positive revenue growth trajectory")
        
        # Ensure score is within bounds
        final_score = max(1.0, min(10.0, score))
        
        return {
            "status": "success",
            "score": round(final_score, 1),
            "factors": factors
        }
    except Exception as e:
        logger.error(f"Financial score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_traction_score(startup_data: dict, public_data: dict, interview_data: dict) -> dict:
    """Calculate traction evaluation score (1-10)"""
    try:
        score = 5.0  # Base score
        factors = []
        
        # Revenue as traction indicator
        revenue = startup_data.get("revenue", 0)
        if revenue > 5000000:  # $5M+ revenue
            score += 2.5
            factors.append("Excellent revenue traction ($5M+)")
        elif revenue > 1000000:  # $1M+ revenue
            score += 2.0
            factors.append("Strong revenue traction ($1M+)")
        elif revenue > 100000:  # $100K+ revenue
            score += 1.0
            factors.append("Good early revenue traction")
        elif revenue > 0:
            score += 0.5
            factors.append("Initial revenue achieved")
        
        # Funding history as traction indicator
        funding_raised = startup_data.get("funding_raised", 0)
        if funding_raised > 10000000:  # $10M+ raised
            score += 1.5
            factors.append("Significant funding raised ($10M+)")
        elif funding_raised > 1000000:  # $1M+ raised
            score += 1.0
            factors.append("Good funding traction ($1M+)")
        elif funding_raised > 0:
            score += 0.5
            factors.append("Initial funding secured")
        
        # Public presence and mentions
        company_info = public_data.get("company", {})
        news_mentions = len(company_info.get("news_mentions", []))
        funding_history = len(company_info.get("funding_history", []))
        
        if news_mentions > 5:
            score += 1.0
            factors.append("Strong media presence and coverage")
        elif news_mentions > 2:
            score += 0.5
            factors.append("Moderate media attention")
        
        if funding_history > 2:
            score += 0.5
            factors.append("Multiple funding rounds completed")
        
        # Team growth
        team_size = startup_data.get("team_size", 0)
        stage = startup_data.get("stage", "").lower()
        
        if stage == "series a" and team_size > 15:
            score += 0.5
            factors.append("Team scaling indicates growth")
        elif stage == "seed" and team_size > 8:
            score += 0.5
            factors.append("Good team growth for stage")
        
        # Interview traction indicators
        if interview_data:
            positive_signals = interview_data.get("positive_signals", [])
            traction_signals = [s for s in positive_signals if any(word in s.lower() for word in ["traction", "growth", "customer", "partnership"])]
            if traction_signals:
                score += 0.5
                factors.append("Positive traction signals in interview")
        
        # Ensure score is within bounds
        final_score = max(1.0, min(10.0, score))
        
        return {
            "status": "success",
            "score": round(final_score, 1),
            "factors": factors
        }
    except Exception as e:
        logger.error(f"Traction score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def calculate_overall_score(individual_scores: dict) -> dict:
    """Calculate weighted overall investment score"""
    try:
        # Weights for different categories
        weights = {
            "team": 0.25,
            "market": 0.20,
            "product": 0.20,
            "financial": 0.20,
            "traction": 0.15
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for category, weight in weights.items():
            if category in individual_scores:
                weighted_sum += individual_scores[category] * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 5.0
        
        return {
            "status": "success",
            "overall_score": round(overall_score, 1)
        }
    except Exception as e:
        logger.error(f"Overall score calculation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def determine_investment_recommendation(overall_score: float, risks_data: list, individual_scores: dict) -> dict:
    """Determine final investment recommendation based on scores and risks"""
    try:
        # Count critical risks
        red_risks = [r for r in risks_data if r.get("severity") == "red"]
        
        # Base recommendation on overall score
        if overall_score >= 8.0 and len(red_risks) == 0:
            recommendation = "pass"
            reason = "Strong overall performance across all categories with no critical risks"
        elif overall_score >= 7.0 and len(red_risks) <= 1:
            recommendation = "pass"
            reason = "Good overall performance with manageable risk profile"
        elif overall_score >= 6.0 and len(red_risks) <= 2:
            recommendation = "maybe"
            reason = "Moderate performance with some areas of concern requiring further evaluation"
        elif overall_score >= 5.0:
            recommendation = "maybe"
            reason = "Below-average performance but potential for improvement with right conditions"
        else:
            recommendation = "reject"
            reason = "Poor overall performance with significant risks and concerns"
        
        # Adjust based on critical risks
        if len(red_risks) >= 3:
            recommendation = "reject"
            reason = f"Too many critical risks ({len(red_risks)}) make investment inadvisable"
        
        # Determine investment flag color
        if recommendation == "pass":
            flag = "green"
        elif recommendation == "maybe":
            flag = "yellow"
        else:
            flag = "red"
        
        # Suggest investment amount based on stage and performance
        stage = individual_scores.get("startup_data", {}).get("stage", "").lower()
        suggested_amount = 0
        
        if recommendation == "pass":
            if "series a" in stage:
                suggested_amount = 2000000  # $2M
            elif "seed" in stage:
                suggested_amount = 500000   # $500K
            else:
                suggested_amount = 250000   # $250K
        elif recommendation == "maybe":
            if "series a" in stage:
                suggested_amount = 1000000  # $1M
            elif "seed" in stage:
                suggested_amount = 250000   # $250K
            else:
                suggested_amount = 100000   # $100K
        
        return {
            "status": "success",
            "recommendation": recommendation,
            "reason": reason,
            "flag": flag,
            "suggested_amount": suggested_amount
        }
    except Exception as e:
        logger.error(f"Investment recommendation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def identify_strengths_and_weaknesses(individual_scores: dict, score_factors: dict) -> dict:
    """Identify key strengths and weaknesses from the evaluation"""
    try:
        strengths = []
        weaknesses = []
        
        # Analyze individual scores
        for category, score in individual_scores.items():
            if category == "startup_data":
                continue
                
            factors = score_factors.get(f"{category}_factors", [])
            
            if score >= 7.5:
                strengths.extend([f"Strong {category}: {factor}" for factor in factors[:2]])
            elif score <= 4.0:
                weaknesses.extend([f"Weak {category}: {factor}" for factor in factors[:2]])
        
        # Add general strengths and weaknesses
        if individual_scores.get("financial", 0) >= 7:
            strengths.append("Solid financial fundamentals and unit economics")
        if individual_scores.get("team", 0) >= 7:
            strengths.append("Experienced and credible founding team")
        if individual_scores.get("traction", 0) >= 7:
            strengths.append("Strong market traction and growth indicators")
        
        if individual_scores.get("financial", 10) <= 4:
            weaknesses.append("Financial metrics and runway concerns")
        if individual_scores.get("market", 10) <= 4:
            weaknesses.append("Limited market presence and competitive position")
        
        return {
            "status": "success",
            "strengths": strengths[:5],  # Limit to top 5
            "weaknesses": weaknesses[:5]  # Limit to top 5
        }
    except Exception as e:
        logger.error(f"Strengths/weaknesses identification failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_next_steps(recommendation: str, weaknesses: list, risks_data: list) -> dict:
    """Generate recommended next steps based on evaluation results"""
    try:
        next_steps = []
        
        if recommendation == "pass":
            next_steps.extend([
                "Proceed with term sheet preparation",
                "Conduct final due diligence on legal and technical aspects",
                "Schedule follow-up meetings with key team members"
            ])
        elif recommendation == "maybe":
            next_steps.extend([
                "Request additional financial documentation and projections",
                "Conduct deeper market analysis and competitive assessment",
                "Schedule extended founder interviews to address concerns"
            ])
            
            # Add specific steps based on weaknesses
            if any("financial" in w.lower() for w in weaknesses):
                next_steps.append("Review detailed financial model and unit economics")
            if any("team" in w.lower() for w in weaknesses):
                next_steps.append("Evaluate team composition and hiring plans")
            if any("market" in w.lower() for w in weaknesses):
                next_steps.append("Analyze market size and competitive positioning")
        else:
            next_steps.extend([
                "Decline investment opportunity",
                "Provide constructive feedback to founders",
                "Consider future re-evaluation after addressing key concerns"
            ])
        
        # Add risk-specific steps
        red_risks = [r for r in risks_data if r.get("severity") == "red"]
        for risk in red_risks[:2]:  # Top 2 critical risks
            mitigation = risk.get("mitigation_suggestions", "")
            if mitigation:
                next_steps.append(f"Address critical risk: {mitigation}")
        
        return {
            "status": "success",
            "next_steps": next_steps[:6]  # Limit to 6 steps
        }
    except Exception as e:
        logger.error(f"Next steps generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the FinalEvaluationAgent using Google ADK
final_evaluation_agent = Agent(
    name="final_evaluation_agent",
    model="gemini-2.0-flash",
    description="Agent specialized in synthesizing all analysis data into final investment recommendations",
    instruction="""
    You are the final evaluation agent responsible for synthesizing all startup analysis data into comprehensive investment recommendations.
    
    Your role is to:
    
    1. **Calculate Category Scores** (1-10 scale)
       - Team Score: Founder experience, team composition, credibility
       - Market Score: Market presence, competitive position, benchmarks
       - Product Score: Revenue, growth, customer retention, product-market fit
       - Financial Score: Unit economics, runway, financial risks
       - Traction Score: Revenue growth, funding history, market presence
    
    2. **Calculate Overall Score**
       - Weighted average of category scores
       - Team (25%), Market (20%), Product (20%), Financial (20%), Traction (15%)
    
    3. **Determine Investment Recommendation**
       - PASS (8.0+ overall, no critical risks): Strong investment opportunity
       - CONDITIONAL (6.0-7.9, manageable risks): Requires further evaluation
       - REJECT (<6.0 or critical risks): Not suitable for investment
    
    4. **Generate Investment Flags**
       - Green: Strong recommendation
       - Yellow: Conditional recommendation
       - Red: Not recommended
    
    5. **Identify Key Factors**
       - Strengths: Top performing areas and positive indicators
       - Weaknesses: Areas of concern requiring attention
       - Next Steps: Recommended actions based on evaluation
    
    6. **Suggest Investment Amount**
       - Based on stage, performance, and risk profile
       - Aligned with recommendation level
    
    Use all available data from previous agents to make informed, data-driven investment decisions.
    Provide clear rationale for all recommendations and scores.
    """,
    tools=[
        calculate_team_score,
        calculate_market_score,
        calculate_product_score,
        calculate_financial_score,
        calculate_traction_score,
        calculate_overall_score,
        determine_investment_recommendation,
        identify_strengths_and_weaknesses,
        generate_next_steps
    ]
)
