import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents import Agent

from ..models.pydantic_models import (
    MemoAgentInput,
    MemoAgentOutput
)
from ..services.gcs_service import gcs_service, get_memo_path

logger = logging.getLogger(__name__)

def generate_executive_summary(startup_data: dict, evaluation_data: dict) -> dict:
    """Generate executive summary section of the memo"""
    try:
        startup_name = startup_data.get("name", "Unknown Company")
        sector = startup_data.get("sector", "Unknown")
        stage = startup_data.get("stage", "Unknown")
        
        summary = f"""## Executive Summary

**Company:** {startup_name}
**Sector:** {sector}
**Stage:** {stage}
**Investment Recommendation:** {evaluation_data.get("recommendation", "Under Review")}

{startup_data.get("description", "Company description not available.")}

**Key Highlights:**
- Founded in {startup_data.get("founded_year", "Unknown")}
- Team size: {startup_data.get("team_size", "Unknown")} employees
- Location: {startup_data.get("location", "Unknown")}
"""
        
        if startup_data.get("revenue"):
            summary += f"- Annual Revenue: ${startup_data['revenue']:,.0f}\n"
        if startup_data.get("funding_raised"):
            summary += f"- Total Funding Raised: ${startup_data['funding_raised']:,.0f}\n"
        
        return {"status": "success", "content": summary}
    except Exception as e:
        logger.error(f"Executive summary generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_market_analysis(startup_data: dict, benchmark_data: dict, public_data: dict) -> dict:
    """Generate market analysis section"""
    try:
        sector = startup_data.get("sector", "Unknown")
        
        analysis = f"""## Market Analysis

**Market Sector:** {sector}

### Market Position
"""
        
        # Add market presence information
        company_info = public_data.get("company", {})
        market_presence = company_info.get("market_presence", 0)
        
        if market_presence > 0.7:
            analysis += "- Strong market presence with significant online visibility\n"
        elif market_presence > 0.4:
            analysis += "- Moderate market presence with growing visibility\n"
        else:
            analysis += "- Limited market presence, early-stage visibility\n"
        
        # Add competitive landscape
        analysis += "\n### Competitive Landscape\n"
        
        high_competition_sectors = ["SaaS", "E-commerce", "FinTech"]
        if sector in high_competition_sectors:
            analysis += f"- {sector} is a highly competitive market with established players\n"
            analysis += "- Differentiation and unique value proposition are critical\n"
        else:
            analysis += f"- {sector} market presents opportunities for innovation\n"
        
        # Add benchmark comparisons
        analysis += "\n### Performance vs. Benchmarks\n"
        
        for benchmark in benchmark_data:
            metric_name = benchmark.get("metric_name", "")
            comparison = benchmark.get("comparison_result", "unknown")
            
            if comparison == "above":
                analysis += f"- {metric_name.upper()}: Above industry benchmark ✓\n"
            elif comparison == "below":
                analysis += f"- {metric_name.upper()}: Below industry benchmark ⚠️\n"
            else:
                analysis += f"- {metric_name.upper()}: Within industry range\n"
        
        return {"status": "success", "content": analysis}
    except Exception as e:
        logger.error(f"Market analysis generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_team_assessment(founders_data: list, startup_data: dict) -> dict:
    """Generate team assessment section"""
    try:
        assessment = """## Team Assessment

### Founding Team
"""
        
        if not founders_data:
            assessment += "- Founder information not available for detailed assessment\n"
        else:
            for founder in founders_data:
                name = founder.get("name", "Unknown")
                role = founder.get("role", "Unknown")
                experience = founder.get("years_experience", 0)
                
                assessment += f"\n**{name}** - {role}\n"
                if founder.get("background"):
                    assessment += f"- Background: {founder['background']}\n"
                if founder.get("education"):
                    assessment += f"- Education: {founder['education']}\n"
                if experience:
                    assessment += f"- Experience: {experience} years\n"
                if founder.get("linkedin"):
                    assessment += f"- LinkedIn: {founder['linkedin']}\n"
        
        # Team size analysis
        team_size = startup_data.get("team_size", 0)
        stage = startup_data.get("stage", "").lower()
        
        assessment += f"\n### Team Size & Composition\n"
        assessment += f"- Current team size: {team_size} employees\n"
        
        if stage in ["seed", "series a"] and team_size < 5:
            assessment += "- Team size may be small for current stage\n"
            assessment += "- Consider strategic hires in key areas\n"
        elif team_size > 20 and stage in ["pre-seed", "seed"]:
            assessment += "- Large team for early stage - monitor burn rate\n"
        else:
            assessment += "- Team size appropriate for current stage\n"
        
        return {"status": "success", "content": assessment}
    except Exception as e:
        logger.error(f"Team assessment generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_financial_analysis(startup_data: dict, risks_data: list) -> dict:
    """Generate financial analysis section"""
    try:
        analysis = """## Financial Analysis

### Key Metrics
"""
        
        # Revenue metrics
        revenue = startup_data.get("revenue")
        arr = startup_data.get("arr")
        
        if revenue:
            analysis += f"- Annual Revenue: ${revenue:,.0f}\n"
        if arr:
            analysis += f"- Annual Recurring Revenue: ${arr:,.0f}\n"
        
        # Unit economics
        cac = startup_data.get("cac")
        ltv = startup_data.get("ltv")
        
        if cac and ltv:
            ltv_cac_ratio = ltv / cac if cac > 0 else 0
            analysis += f"- Customer Acquisition Cost: ${cac:,.0f}\n"
            analysis += f"- Lifetime Value: ${ltv:,.0f}\n"
            analysis += f"- LTV/CAC Ratio: {ltv_cac_ratio:.1f}x\n"
            
            if ltv_cac_ratio >= 3:
                analysis += "  - ✓ Healthy unit economics\n"
            else:
                analysis += "  - ⚠️ Unit economics need improvement\n"
        
        # Growth and churn
        growth_rate = startup_data.get("growth_rate")
        churn_rate = startup_data.get("churn_rate")
        
        if growth_rate:
            analysis += f"- Monthly Growth Rate: {growth_rate*100:.1f}%\n"
        if churn_rate:
            analysis += f"- Monthly Churn Rate: {churn_rate*100:.1f}%\n"
        
        # Funding and runway
        funding_raised = startup_data.get("funding_raised")
        burn_rate = startup_data.get("burn_rate")
        runway_months = startup_data.get("runway_months")
        
        analysis += "\n### Funding & Runway\n"
        
        if funding_raised:
            analysis += f"- Total Funding Raised: ${funding_raised:,.0f}\n"
        if burn_rate:
            analysis += f"- Monthly Burn Rate: ${burn_rate:,.0f}\n"
        if runway_months:
            analysis += f"- Runway: {runway_months} months\n"
            
            if runway_months < 6:
                analysis += "  - ⚠️ Critical: Immediate funding needed\n"
            elif runway_months < 12:
                analysis += "  - ⚠️ Should begin fundraising soon\n"
            else:
                analysis += "  - ✓ Adequate runway\n"
        
        # Financial risks
        financial_risks = [r for r in risks_data if r.get("category") == "financial"]
        if financial_risks:
            analysis += "\n### Financial Risk Factors\n"
            for risk in financial_risks:
                severity_icon = "🔴" if risk.get("severity") == "red" else "🟡" if risk.get("severity") == "yellow" else "🟢"
                analysis += f"- {severity_icon} {risk.get('description', 'Unknown risk')}\n"
        
        return {"status": "success", "content": analysis}
    except Exception as e:
        logger.error(f"Financial analysis generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_risk_assessment(risks_data: list) -> dict:
    """Generate risk assessment section"""
    try:
        assessment = """## Risk Assessment

### Risk Overview
"""
        
        if not risks_data:
            assessment += "- No significant risks identified in current analysis\n"
            return {"status": "success", "content": assessment}
        
        # Categorize risks by severity
        red_risks = [r for r in risks_data if r.get("severity") == "red"]
        yellow_risks = [r for r in risks_data if r.get("severity") == "yellow"]
        green_risks = [r for r in risks_data if r.get("severity") == "green"]
        
        assessment += f"- Total Risks Identified: {len(risks_data)}\n"
        assessment += f"- High Risk (Red): {len(red_risks)}\n"
        assessment += f"- Medium Risk (Yellow): {len(yellow_risks)}\n"
        assessment += f"- Low Risk (Green): {len(green_risks)}\n"
        
        # Detail high-priority risks
        if red_risks:
            assessment += "\n### High Priority Risks 🔴\n"
            for risk in red_risks:
                assessment += f"\n**{risk.get('risk_type', 'Unknown').replace('_', ' ').title()}**\n"
                assessment += f"- {risk.get('description', 'No description')}\n"
                assessment += f"- Impact: {risk.get('impact_score', 'Unknown')}/10\n"
                assessment += f"- Likelihood: {risk.get('likelihood_score', 'Unknown')}/10\n"
                if risk.get('mitigation_suggestions'):
                    assessment += f"- Mitigation: {risk['mitigation_suggestions']}\n"
        
        # Detail medium-priority risks
        if yellow_risks:
            assessment += "\n### Medium Priority Risks 🟡\n"
            for risk in yellow_risks:
                assessment += f"\n**{risk.get('risk_type', 'Unknown').replace('_', ' ').title()}**\n"
                assessment += f"- {risk.get('description', 'No description')}\n"
                if risk.get('mitigation_suggestions'):
                    assessment += f"- Mitigation: {risk['mitigation_suggestions']}\n"
        
        return {"status": "success", "content": assessment}
    except Exception as e:
        logger.error(f"Risk assessment generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def generate_investment_recommendation(evaluation_data: dict, startup_data: dict) -> dict:
    """Generate investment recommendation section"""
    try:
        recommendation = """## Investment Recommendation

"""
        
        overall_score = evaluation_data.get("overall_score", 0)
        rec = evaluation_data.get("recommendation", "under_review")
        reason = evaluation_data.get("recommendation_reason", "")
        
        # Recommendation header
        if rec == "pass":
            recommendation += "### ✅ RECOMMEND INVESTMENT\n"
        elif rec == "maybe":
            recommendation += "### ⚠️ CONDITIONAL RECOMMENDATION\n"
        else:
            recommendation += "### ❌ DO NOT RECOMMEND\n"
        
        recommendation += f"\n**Overall Score:** {overall_score}/10\n"
        
        if reason:
            recommendation += f"\n**Rationale:** {reason}\n"
        
        # Investment amount
        suggested_amount = evaluation_data.get("investment_amount_suggested")
        if suggested_amount:
            recommendation += f"\n**Suggested Investment Amount:** ${suggested_amount:,.0f}\n"
        
        # Strengths and weaknesses
        strengths = evaluation_data.get("strengths", [])
        weaknesses = evaluation_data.get("weaknesses", [])
        
        if strengths:
            recommendation += "\n### Key Strengths\n"
            for strength in strengths:
                recommendation += f"- {strength}\n"
        
        if weaknesses:
            recommendation += "\n### Areas of Concern\n"
            for weakness in weaknesses:
                recommendation += f"- {weakness}\n"
        
        # Next steps
        next_steps = evaluation_data.get("next_steps", [])
        if next_steps:
            recommendation += "\n### Recommended Next Steps\n"
            for step in next_steps:
                recommendation += f"- {step}\n"
        
        return {"status": "success", "content": recommendation}
    except Exception as e:
        logger.error(f"Investment recommendation generation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def compile_full_memo(sections: dict, startup_data: dict) -> dict:
    """Compile all sections into a complete investment memo"""
    try:
        startup_name = startup_data.get("name", "Unknown Company")
        current_date = datetime.now().strftime("%B %d, %Y")
        
        memo = f"""# Investment Memo: {startup_name}

**Date:** {current_date}
**Prepared by:** AI Investment Analysis System

---

{sections.get('executive_summary', '')}

{sections.get('market_analysis', '')}

{sections.get('team_assessment', '')}

{sections.get('financial_analysis', '')}

{sections.get('risk_assessment', '')}

{sections.get('investment_recommendation', '')}

---

*This memo was generated using automated analysis. Please conduct additional due diligence before making investment decisions.*
"""
        
        return {"status": "success", "memo_content": memo}
    except Exception as e:
        logger.error(f"Memo compilation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def save_memo_to_gcs(startup_id: int, memo_content: str, format: str = "md") -> dict:
    """Save the investment memo to Google Cloud Storage"""
    try:
        gcs_path = get_memo_path(startup_id, format)
        
        if format == "md":
            content_type = "text/markdown"
        else:
            content_type = "text/plain"
        
        # Upload to GCS
        gcs_service.upload_text(
            memo_content, 
            gcs_path.replace("gs://", "").split("/", 1)[1],
            content_type
        )
        
        logger.info(f"Memo saved to GCS: {gcs_path}")
        return {"status": "success", "gcs_path": gcs_path}
    except Exception as e:
        logger.error(f"Failed to save memo to GCS: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the MemoAgent using Google ADK
memo_agent = Agent(
    name="investment_memo_agent",
    model="gemini-2.0-flash",
    description="Agent specialized in generating comprehensive investment memos for startup evaluation",
    instruction="""
    You are an expert investment analyst agent responsible for creating comprehensive investment memos.
    
    Your role is to synthesize all available data about a startup into a professional investment memo that includes:
    
    1. **Executive Summary**
       - Company overview and key highlights
       - Investment recommendation summary
       - Key metrics and achievements
    
    2. **Market Analysis**
       - Market position and competitive landscape
       - Industry benchmarks and comparisons
       - Market opportunity assessment
    
    3. **Team Assessment**
       - Founder backgrounds and experience
       - Team composition and capabilities
       - Leadership evaluation
    
    4. **Financial Analysis**
       - Revenue and growth metrics
       - Unit economics (CAC/LTV)
       - Funding history and runway
       - Financial risk factors
    
    5. **Risk Assessment**
       - Categorized risk analysis
       - Risk severity and mitigation strategies
       - Overall risk profile
    
    6. **Investment Recommendation**
       - Clear recommendation (invest/conditional/pass)
       - Investment rationale and reasoning
       - Suggested investment amount
       - Next steps and conditions
    
    Generate professional, well-structured memos that provide clear investment guidance.
    Use the available tools to create each section and compile the final memo.
    """,
    tools=[
        generate_executive_summary,
        generate_market_analysis,
        generate_team_assessment,
        generate_financial_analysis,
        generate_risk_assessment,
        generate_investment_recommendation,
        compile_full_memo,
        save_memo_to_gcs
    ]
)
