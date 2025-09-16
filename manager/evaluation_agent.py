"""
Startup Evaluation Agent - Python Implementation
AI agent for comprehensive startup evaluation using Vertex AI
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import requests
from google.cloud import firestore
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part
import vertexai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationCriteria(Enum):
    FOUNDER_MARKET_FIT = "founder_market_fit"
    PROBLEM_EVALUATION = "problem_evaluation"
    USP_EVALUATION = "usp_evaluation"
    TEAM_PROFILE = "team_profile"

@dataclass
class EvaluationResult:
    startup_id: str
    scores: Dict[str, float]
    analysis: Dict[str, Any]
    recommendations: List[str]
    risk_factors: List[str]
    confidence_score: float
    timestamp: datetime

class StartupEvaluationAgent:
    """Main evaluation agent for startup analysis"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        
        # Initialize Firestore
        self.db = firestore.Client()
        
        # Evaluation weights
        self.criteria_weights = {
            EvaluationCriteria.FOUNDER_MARKET_FIT: 0.25,
            EvaluationCriteria.PROBLEM_EVALUATION: 0.25,
            EvaluationCriteria.USP_EVALUATION: 0.25,
            EvaluationCriteria.TEAM_PROFILE: 0.25
        }
    
    async def evaluate_startup(self, startup_data: Dict[str, Any]) -> EvaluationResult:
        """Main evaluation method"""
        logger.info(f"Starting evaluation for startup: {startup_data.get('name')}")
        
        try:
            # Step 1: Extract and structure data
            structured_data = await self._extract_key_data(startup_data)
            
            # Step 2: Conduct web research
            research_data = await self._conduct_web_research(structured_data)
            
            # Step 3: Analyze each criterion
            founder_score = await self._evaluate_founder_market_fit(structured_data, research_data)
            problem_score = await self._evaluate_problem_and_competition(structured_data, research_data)
            usp_score = await self._evaluate_usp(structured_data, research_data)
            team_score = await self._evaluate_team_profile(structured_data, research_data)
            
            # Step 4: Calculate overall score
            scores = {
                "founder_market_fit": founder_score,
                "problem_evaluation": problem_score,
                "usp_evaluation": usp_score,
                "team_profile": team_score
            }
            
            overall_score = sum(
                scores[criterion.value] * weight 
                for criterion, weight in self.criteria_weights.items()
            )
            scores["overall_score"] = overall_score
            
            # Step 5: Generate recommendations and risk factors
            recommendations = await self._generate_recommendations(scores, structured_data, research_data)
            risk_factors = await self._identify_risk_factors(scores, structured_data, research_data)
            
            # Step 6: Calculate confidence score
            confidence_score = await self._calculate_confidence_score(structured_data, research_data)
            
            result = EvaluationResult(
                startup_id=startup_data.get('startup_id'),
                scores=scores,
                analysis={
                    'structured_data': structured_data,
                    'research_data': research_data
                },
                recommendations=recommendations,
                risk_factors=risk_factors,
                confidence_score=confidence_score,
                timestamp=datetime.utcnow()
            )
            
            # Save results to Firestore
            await self._save_evaluation_result(result)
            
            logger.info(f"Evaluation completed. Overall score: {overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise
    
    async def _extract_key_data(self, startup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure key information from startup data"""
        
        prompt = f"""
        Analyze the following startup information and extract key structured data:
        
        Startup Data: {json.dumps(startup_data, indent=2)}
        
        Please extract and structure the following information:
        1. Company basics (name, industry, stage, location)
        2. Problem statement and target market
        3. Solution description and unique value proposition
        4. Founder backgrounds and experience
        5. Team composition and skills
        6. Business model and revenue streams
        7. Competition and market positioning
        8. Traction and key metrics
        
        Return the response as a structured JSON object.
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            # Parse the JSON response
            structured_data = json.loads(response.text)
            return structured_data
        except json.JSONDecodeError:
            # Fallback: create basic structure
            return {
                "company_basics": startup_data.get('startup_info', {}),
                "founders": startup_data.get('founders', []),
                "extracted_at": datetime.utcnow().isoformat()
            }
    
    async def _conduct_web_research(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive web research"""
        
        company_name = structured_data.get('company_basics', {}).get('name', '')
        industry = structured_data.get('company_basics', {}).get('industry', '')
        
        research_queries = [
            f"{company_name} startup funding news",
            f"{company_name} competitors market analysis",
            f"{industry} market size trends 2024",
            f"{company_name} founder background linkedin"
        ]
        
        research_results = {}
        
        for query in research_queries:
            try:
                # Simulate web search (replace with actual search API)
                search_results = await self._search_web(query)
                research_results[query] = search_results
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {str(e)}")
                research_results[query] = {"error": str(e)}
        
        return {
            "queries": research_queries,
            "results": research_results,
            "researched_at": datetime.utcnow().isoformat()
        }
    
    async def _search_web(self, query: str) -> Dict[str, Any]:
        """Simulate web search - replace with actual search API"""
        # This is a placeholder - implement actual web search
        return {
            "query": query,
            "results": [
                {"title": f"Sample result for {query}", "url": "https://example.com", "snippet": "Sample snippet"}
            ]
        }
    
    async def _evaluate_founder_market_fit(self, structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> float:
        """Evaluate founder-market fit (0-100 score)"""
        
        prompt = f"""
        Evaluate the founder-market fit for this startup based on the following criteria:
        
        Structured Data: {json.dumps(structured_data, indent=2)}
        Research Data: {json.dumps(research_data, indent=2)}
        
        Evaluation Criteria:
        1. Domain Expertise (40%): Founder's knowledge and experience in the target market
        2. Previous Experience (30%): Relevant startup, industry, or leadership experience
        3. Network Strength (30%): Connections and relationships in the industry
        
        Provide a score from 0-100 and detailed reasoning for each criterion.
        Return as JSON: {{"score": 75, "reasoning": {{"domain_expertise": "...", "previous_experience": "...", "network_strength": "..."}}}}
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            result = json.loads(response.text)
            return float(result.get('score', 50))
        except:
            return 50.0  # Default score if parsing fails
    
    async def _evaluate_problem_and_competition(self, structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> float:
        """Evaluate problem validation and competitive landscape"""
        
        prompt = f"""
        Evaluate the problem and competition for this startup:
        
        Data: {json.dumps(structured_data, indent=2)}
        Research: {json.dumps(research_data, indent=2)}
        
        Criteria:
        1. Market Size (40%): Total addressable market and growth potential
        2. Problem Urgency (30%): How critical is the problem being solved
        3. Competition Analysis (30%): Competitive landscape and differentiation
        
        Score 0-100 with reasoning.
        Return JSON: {{"score": 80, "reasoning": {{"market_size": "...", "problem_urgency": "...", "competition": "..."}}}}
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            result = json.loads(response.text)
            return float(result.get('score', 50))
        except:
            return 50.0
    
    async def _evaluate_usp(self, structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> float:
        """Evaluate unique selling proposition"""
        
        prompt = f"""
        Evaluate the USP and competitive advantage:
        
        Data: {json.dumps(structured_data, indent=2)}
        
        Criteria:
        1. Uniqueness (40%): How unique is the solution
        2. Defensibility (30%): Barriers to entry and IP protection
        3. Scalability (30%): Ability to scale the solution
        
        Score 0-100 with reasoning.
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            result = json.loads(response.text)
            return float(result.get('score', 50))
        except:
            return 50.0
    
    async def _evaluate_team_profile(self, structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> float:
        """Evaluate overall team profile"""
        
        prompt = f"""
        Evaluate the team composition and capabilities:
        
        Data: {json.dumps(structured_data, indent=2)}
        
        Criteria:
        1. Technical Skills (40%): Technical expertise and capabilities
        2. Business Acumen (30%): Business and commercial skills
        3. Team Dynamics (30%): Team composition and working relationships
        
        Score 0-100 with reasoning.
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            result = json.loads(response.text)
            return float(result.get('score', 50))
        except:
            return 50.0
    
    async def _generate_recommendations(self, scores: Dict[str, float], structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> List[str]:
        """Generate investment recommendations"""
        
        prompt = f"""
        Based on the evaluation scores and analysis, generate 3-5 key recommendations:
        
        Scores: {json.dumps(scores, indent=2)}
        
        Focus on:
        - Investment decision (invest/pass/more info needed)
        - Key strengths to leverage
        - Critical areas for improvement
        - Next steps for due diligence
        
        Return as JSON array: ["recommendation 1", "recommendation 2", ...]
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            recommendations = json.loads(response.text)
            return recommendations if isinstance(recommendations, list) else []
        except:
            return ["Further analysis required", "Schedule founder interview"]
    
    async def _identify_risk_factors(self, scores: Dict[str, float], structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> List[str]:
        """Identify key risk factors"""
        
        prompt = f"""
        Identify 3-5 key risk factors based on the evaluation:
        
        Scores: {json.dumps(scores, indent=2)}
        
        Consider:
        - Market risks
        - Execution risks
        - Team risks
        - Competitive risks
        - Financial risks
        
        Return as JSON array: ["risk 1", "risk 2", ...]
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            risks = json.loads(response.text)
            return risks if isinstance(risks, list) else []
        except:
            return ["Market competition", "Execution risk"]
    
    async def _calculate_confidence_score(self, structured_data: Dict[str, Any], research_data: Dict[str, Any]) -> float:
        """Calculate confidence in the evaluation"""
        
        # Factors affecting confidence
        data_completeness = len(structured_data.keys()) / 8  # Assuming 8 key data points
        research_quality = len(research_data.get('results', {})) / 4  # 4 research queries
        
        confidence = min(100, (data_completeness + research_quality) * 50)
        return confidence
    
    async def _save_evaluation_result(self, result: EvaluationResult):
        """Save evaluation result to Firestore"""
        
        doc_ref = self.db.collection('evaluations').document(result.startup_id)
        
        evaluation_data = {
            'startup_id': result.startup_id,
            'scores': result.scores,
            'recommendations': result.recommendations,
            'risk_factors': result.risk_factors,
            'confidence_score': result.confidence_score,
            'status': 'completed',
            'completed_at': result.timestamp,
            'updated_at': result.timestamp
        }
        
        doc_ref.set(evaluation_data, merge=True)
        logger.info(f"Evaluation result saved for startup: {result.startup_id}")

# Usage example
async def main():
    """Example usage of the evaluation agent"""
    
    agent = StartupEvaluationAgent(project_id="your-project-id")
    
    sample_startup_data = {
        "startup_id": "test-startup-123",
        "startup_info": {
            "name": "TechStartup Inc",
            "description": "AI-powered solution for small businesses",
            "industry": "Technology",
            "stage": "Seed",
            "location": "San Francisco, CA"
        },
        "founders": [
            {
                "name": "John Doe",
                "background": "Former Google engineer with 10 years experience",
                "email": "john@techstartup.com"
            }
        ]
    }
    
    result = await agent.evaluate_startup(sample_startup_data)
    print(f"Evaluation completed with overall score: {result.scores['overall_score']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
