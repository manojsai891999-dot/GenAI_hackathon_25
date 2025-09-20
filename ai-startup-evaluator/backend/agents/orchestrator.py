import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.adk.agents import SequentialAgent, Agent
from google.adk.core import BaseAgent

from .extractor_agent import extractor_agent
from .public_data_extractor_agent import public_data_extractor_agent
from .risk_agent import risk_agent
from .memo_agent import memo_agent
from .meeting_scheduler_agent import meeting_scheduler_agent
from .voice_interview_agent import voice_interview_agent
from .audio_interview_agent import audio_interview_agent
from .final_evaluation_agent import final_evaluation_agent

from ..models.pydantic_models import (
    StartupCreate, FounderCreate, BenchmarkCreate, RiskCreate,
    InterviewCreate, FinalEvaluationCreate
)
from ..models.database import get_db
from ..models import schemas
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class StartupEvaluationOrchestrator:
    """Orchestrates the complete startup evaluation workflow using Google ADK agents"""
    
    def __init__(self):
        self.agents = {
            "extractor": extractor_agent,
            "public_data": public_data_extractor_agent,
            "risk": risk_agent,
            "memo": memo_agent,
            "meeting_scheduler": meeting_scheduler_agent,
            "voice_interview": voice_interview_agent,  # For processing uploaded audio pitches
            "audio_interview": audio_interview_agent,  # For conducting live interviews
            "final_evaluation": final_evaluation_agent
        }
        
        # Create sequential workflow for main evaluation pipeline
        self.main_workflow = SequentialAgent(
            name="startup_evaluation_workflow",
            agents=[
                extractor_agent,
                public_data_extractor_agent,
                risk_agent,
                final_evaluation_agent,
                memo_agent,
                meeting_scheduler_agent
            ],
            description="Complete startup evaluation pipeline from data extraction to meeting scheduling"
        )
    
    async def process_startup_evaluation(
        self,
        pitch_deck_files: List[str] = None,
        audio_files: List[str] = None,
        video_files: List[str] = None,
        startup_id: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Process complete startup evaluation workflow with multiple file types
        
        Args:
            pitch_deck_files: List of paths to pitch deck files (PDF, PPT, PPTX)
            audio_files: List of paths to audio pitch files (MP3, WAV, M4A, etc.)
            video_files: List of paths to video presentation files (MP4, MOV, etc.)
            startup_id: Optional existing startup ID
            db: Database session
        
        Returns:
            Complete evaluation results including meeting scheduling
        """
        try:
            all_files = (pitch_deck_files or []) + (audio_files or []) + (video_files or [])
            logger.info(f"Starting startup evaluation workflow for {len(all_files)} files")
            
            # Step 1: Extract startup data from all files
            extraction_result = await self._run_extractor_agent_multi_file(
                pitch_deck_files or [], audio_files or [], video_files or []
            )
            if not extraction_result["success"]:
                return extraction_result
            
            # Save startup and founders to database
            if db:
                startup_id = await self._save_startup_to_db(
                    extraction_result["data"], db, startup_id
                )
            
            # Step 2: Extract public data and benchmarks
            public_data_result = await self._run_public_data_agent(
                startup_id, extraction_result["data"]
            )
            
            # Save benchmarks to database
            if db and public_data_result["success"]:
                await self._save_benchmarks_to_db(
                    public_data_result["data"]["benchmarks"], db
                )
            
            # Step 3: Analyze risks
            risk_result = await self._run_risk_agent(
                startup_id,
                extraction_result["data"],
                public_data_result["data"] if public_data_result["success"] else {}
            )
            
            # Save risks to database
            if db and risk_result["success"]:
                await self._save_risks_to_db(risk_result["data"]["risks"], db)
            
            # Step 4: Process audio pitch files (if any)
            audio_analysis_result = None
            if audio_files:
                audio_analysis_result = await self._run_voice_interview_agent_multi_audio(
                    startup_id, audio_files
                )
                
                # Save audio analysis to database
                if db and audio_analysis_result["success"]:
                    await self._save_interview_to_db(audio_analysis_result["data"], db)
            
            # Step 5: Generate final evaluation
            final_evaluation_result = await self._run_final_evaluation_agent(
                startup_id,
                extraction_result["data"],
                public_data_result["data"] if public_data_result["success"] else {},
                risk_result["data"] if risk_result["success"] else {},
                audio_analysis_result["data"] if audio_analysis_result and audio_analysis_result["success"] else {}
            )
            
            # Save final evaluation to database
            if db and final_evaluation_result["success"]:
                await self._save_final_evaluation_to_db(
                    final_evaluation_result["data"], db
                )
            
            # Step 6: Generate investment memo
            memo_result = await self._run_memo_agent(
                startup_id,
                {
                    "startup": extraction_result["data"],
                    "public_data": public_data_result["data"] if public_data_result["success"] else {},
                    "risks": risk_result["data"] if risk_result["success"] else {},
                    "audio_analysis": audio_analysis_result["data"] if audio_analysis_result and audio_analysis_result["success"] else {},
                    "evaluation": final_evaluation_result["data"] if final_evaluation_result["success"] else {}
                }
            )
            
            # Step 7: Schedule meeting based on evaluation results
            meeting_result = await self._run_meeting_scheduler_agent(
                startup_id,
                extraction_result["data"],
                memo_result["data"] if memo_result["success"] else {},
                final_evaluation_result["data"] if final_evaluation_result["success"] else {}
            )
            
            # Compile final results
            final_results = {
                "success": True,
                "startup_id": startup_id,
                "results": {
                    "extraction": extraction_result,
                    "public_data": public_data_result,
                    "risks": risk_result,
                    "final_evaluation": final_evaluation_result,
                    "memo": memo_result,
                    "meeting_scheduled": meeting_result
                }
            }
            
            if audio_analysis_result:
                final_results["results"]["audio_analysis"] = audio_analysis_result
            
            logger.info(f"Startup evaluation workflow completed successfully for startup ID: {startup_id}")
            return final_results
            
        except Exception as e:
            logger.error(f"Startup evaluation workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "startup_id": startup_id
            }
    
    async def _run_extractor_agent(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Run the extractor agent"""
        try:
            # Use ADK agent to process the extraction
            prompt = f"""
            Extract startup information from the provided {file_type} file at path: {file_path}
            
            Use the extract_text_from_pdf or extract_text_from_pptx tools to read the file content,
            then use extract_startup_data to analyze the content and validate_startup_data to clean the results.
            
            Return the extracted startup and founder information in a structured format.
            """
            
            response = await extractor_agent.run(prompt)
            
            # Parse the agent response (this would be more sophisticated in practice)
            return {
                "success": True,
                "data": {
                    "startup": {},  # Would be populated from agent response
                    "founders": [],  # Would be populated from agent response
                    "confidence": 0.8,
                    "extracted_fields": [],
                    "missing_fields": []
                }
            }
        except Exception as e:
            logger.error(f"Extractor agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_public_data_agent(self, startup_id: int, startup_data: Dict) -> Dict[str, Any]:
        """Run the public data extractor agent"""
        try:
            prompt = f"""
            Extract public data and benchmarks for startup ID {startup_id}.
            
            Startup data: {json.dumps(startup_data, indent=2)}
            
            Use the available tools to:
            1. Search for founder information and credibility
            2. Extract company information and market presence
            3. Get sector benchmarks and comparisons
            4. Analyze the data with AI insights
            
            Return comprehensive public data and benchmark comparisons.
            """
            
            response = await public_data_extractor_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "benchmarks": [],  # Would be populated from agent response
                    "public_data": {},  # Would be populated from agent response
                    "confidence": 0.7
                }
            }
        except Exception as e:
            logger.error(f"Public data agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_risk_agent(self, startup_id: int, startup_data: Dict, public_data: Dict) -> Dict[str, Any]:
        """Run the risk analysis agent"""
        try:
            prompt = f"""
            Analyze investment risks for startup ID {startup_id}.
            
            Startup data: {json.dumps(startup_data, indent=2)}
            Public data: {json.dumps(public_data, indent=2)}
            
            Use the available tools to analyze:
            1. Financial risks (burn rate, runway, unit economics)
            2. Team risks (experience, size, composition)
            3. Market risks (competition, presence, positioning)
            4. Product risks (traction, churn, product-market fit)
            5. Regulatory risks (compliance, legal challenges)
            
            Calculate overall risk score and provide mitigation suggestions.
            """
            
            response = await risk_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "risks": [],  # Would be populated from agent response
                    "overall_risk_score": 5.0,
                    "risk_summary": "Risk analysis completed"
                }
            }
        except Exception as e:
            logger.error(f"Risk agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_voice_interview_agent(self, startup_id: int, voice_file_path: str) -> Dict[str, Any]:
        """Run the voice interview analysis agent"""
        try:
            prompt = f"""
            Process voice interview for startup ID {startup_id} from audio file: {voice_file_path}
            
            Use the available tools to:
            1. Convert audio to processable format
            2. Transcribe speech to text
            3. Analyze interview content for insights
            4. Extract key topics and themes
            5. Generate comprehensive interview summary
            6. Save interview data to GCS
            
            Provide sentiment analysis, key insights, and red flags/positive signals.
            """
            
            response = await voice_interview_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "transcript_summary": "",  # Would be populated from agent response
                    "key_insights": [],
                    "sentiment_score": 0.0,
                    "confidence_score": 0.8,
                    "red_flags": [],
                    "positive_signals": []
                }
            }
        except Exception as e:
            logger.error(f"Voice interview agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_final_evaluation_agent(
        self, startup_id: int, startup_data: Dict, public_data: Dict, 
        risk_data: Dict, interview_data: Dict
    ) -> Dict[str, Any]:
        """Run the final evaluation agent"""
        try:
            prompt = f"""
            Generate final investment evaluation for startup ID {startup_id}.
            
            Available data:
            - Startup: {json.dumps(startup_data, indent=2)}
            - Public: {json.dumps(public_data, indent=2)}
            - Risks: {json.dumps(risk_data, indent=2)}
            - Interview: {json.dumps(interview_data, indent=2)}
            
            Use the available tools to:
            1. Calculate individual category scores (team, market, product, financial, traction)
            2. Calculate weighted overall score
            3. Determine investment recommendation (pass/maybe/reject)
            4. Identify key strengths and weaknesses
            5. Generate recommended next steps
            
            Provide comprehensive investment recommendation with clear rationale.
            """
            
            response = await final_evaluation_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "overall_score": 7.0,  # Would be populated from agent response
                    "recommendation": "maybe",
                    "recommendation_reason": "",
                    "strengths": [],
                    "weaknesses": [],
                    "next_steps": []
                }
            }
        except Exception as e:
            logger.error(f"Final evaluation agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_memo_agent(self, startup_id: int, all_data: Dict) -> Dict[str, Any]:
        """Run the memo generation agent"""
        try:
            prompt = f"""
            Generate comprehensive investment memo for startup ID {startup_id}.
            
            All analysis data: {json.dumps(all_data, indent=2)}
            
            Use the available tools to:
            1. Generate executive summary
            2. Create market analysis section
            3. Develop team assessment
            4. Compile financial analysis
            5. Summarize risk assessment
            6. Formulate investment recommendation
            7. Compile full memo and save to GCS
            
            Create a professional, well-structured investment memo.
            """
            
            response = await memo_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "memo_content": "",  # Would be populated from agent response
                    "memo_gcs_path": "",
                    "memo_format": "markdown"
                }
            }
        except Exception as e:
            logger.error(f"Memo agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _save_startup_to_db(self, extraction_data: Dict, db: Session, startup_id: Optional[int] = None) -> int:
        """Save startup and founders to database"""
        try:
            startup_data = extraction_data.get("startup", {})
            founders_data = extraction_data.get("founders", [])
            
            if startup_id:
                # Update existing startup
                startup = db.query(schemas.Startup).filter(schemas.Startup.id == startup_id).first()
                if startup:
                    for key, value in startup_data.items():
                        if hasattr(startup, key) and value is not None:
                            setattr(startup, key, value)
            else:
                # Create new startup
                startup = schemas.Startup(**startup_data)
                db.add(startup)
                db.flush()  # Get the ID
                startup_id = startup.id
            
            # Save founders
            for founder_data in founders_data:
                founder_data["startup_id"] = startup_id
                founder = schemas.Founder(**founder_data)
                db.add(founder)
            
            db.commit()
            return startup_id
            
        except Exception as e:
            logger.error(f"Failed to save startup to database: {str(e)}")
            db.rollback()
            raise
    
    async def _save_benchmarks_to_db(self, benchmarks_data: List[Dict], db: Session):
        """Save benchmarks to database"""
        try:
            for benchmark_data in benchmarks_data:
                benchmark = schemas.Benchmark(**benchmark_data)
                db.add(benchmark)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save benchmarks: {str(e)}")
            db.rollback()
    
    async def _save_risks_to_db(self, risks_data: List[Dict], db: Session):
        """Save risks to database"""
        try:
            for risk_data in risks_data:
                risk = schemas.Risk(**risk_data)
                db.add(risk)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save risks: {str(e)}")
            db.rollback()
    
    async def _save_interview_to_db(self, interview_data: Dict, db: Session):
        """Save interview to database"""
        try:
            interview = schemas.Interview(**interview_data)
            db.add(interview)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save interview: {str(e)}")
            db.rollback()
    
    async def _save_final_evaluation_to_db(self, evaluation_data: Dict, db: Session):
        """Save final evaluation to database"""
        try:
            evaluation = schemas.FinalEvaluation(**evaluation_data)
            db.add(evaluation)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save final evaluation: {str(e)}")
            db.rollback()
    
    async def _run_extractor_agent_multi_file(
        self, pitch_deck_files: List[str], audio_files: List[str], video_files: List[str]
    ) -> Dict[str, Any]:
        """Run the extractor agent with multiple file types"""
        try:
            all_files = pitch_deck_files + audio_files + video_files
            file_info = {
                "pitch_decks": len(pitch_deck_files),
                "audio_files": len(audio_files), 
                "video_files": len(video_files),
                "total_files": len(all_files)
            }
            
            prompt = f"""
            Extract startup information from multiple uploaded files:
            - Pitch deck files: {pitch_deck_files}
            - Audio pitch files: {audio_files}
            - Video presentation files: {video_files}
            
            File summary: {file_info}
            
            Use the appropriate extraction tools for each file type:
            - extract_text_from_pdf/extract_text_from_pptx for pitch decks
            - transcribe_audio for audio files
            - extract_video_content for video files
            
            Then use extract_startup_data to analyze all content and validate_startup_data to clean results.
            Combine insights from all file types to create comprehensive startup profile.
            """
            
            response = await extractor_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "startup": {},  # Would be populated from agent response
                    "founders": [],  # Would be populated from agent response
                    "confidence": 0.8,
                    "extracted_fields": [],
                    "missing_fields": [],
                    "file_analysis": file_info
                }
            }
        except Exception as e:
            logger.error(f"Multi-file extractor agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_voice_interview_agent_multi_audio(
        self, startup_id: int, audio_files: List[str]
    ) -> Dict[str, Any]:
        """Run the voice interview agent for multiple audio pitch files"""
        try:
            prompt = f"""
            Process multiple audio pitch files for startup ID {startup_id}:
            Audio files: {audio_files}
            
            For each audio file:
            1. Convert audio to processable format
            2. Transcribe speech to text
            3. Analyze pitch content for insights
            4. Extract key topics and themes
            5. Assess presentation quality and confidence
            
            Combine analysis from all audio files to generate comprehensive pitch assessment.
            Save processed data to GCS for future reference.
            """
            
            response = await voice_interview_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "transcript_summary": "",  # Combined from all audio files
                    "key_insights": [],
                    "sentiment_score": 0.0,
                    "confidence_score": 0.8,
                    "red_flags": [],
                    "positive_signals": [],
                    "audio_files_processed": len(audio_files)
                }
            }
        except Exception as e:
            logger.error(f"Multi-audio voice interview agent failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _run_meeting_scheduler_agent(
        self, startup_id: int, startup_data: Dict, memo_data: Dict, evaluation_data: Dict
    ) -> Dict[str, Any]:
        """Run the meeting scheduler agent"""
        try:
            prompt = f"""
            Schedule appropriate meeting for startup ID {startup_id} based on evaluation results.
            
            Startup data: {json.dumps(startup_data, indent=2)}
            Memo data: {json.dumps(memo_data, indent=2)}
            Evaluation data: {json.dumps(evaluation_data, indent=2)}
            
            Use the available tools to:
            1. Determine appropriate meeting type based on evaluation score and recommendation
            2. Check calendar availability for optimal scheduling
            3. Create calendar event with proper attendees and materials
            4. Send meeting preparation materials to participants
            
            Meeting types based on evaluation:
            - Investment Committee Presentation (score ≥7, "pass" recommendation)
            - Due Diligence Deep Dive (score 5-7, "maybe" recommendation)  
            - Founder Interview (promising opportunities)
            - Initial Screening Call (early stage evaluation)
            """
            
            response = await meeting_scheduler_agent.run(prompt)
            
            return {
                "success": True,
                "data": {
                    "meeting_scheduled": True,
                    "meeting_type": "Due Diligence Deep Dive",  # Would be determined by agent
                    "scheduled_time": "",  # Would be populated from agent response
                    "calendar_event_id": "",
                    "attendees": [],
                    "materials_prepared": True
                }
            }
        except Exception as e:
            logger.error(f"Meeting scheduler agent failed: {str(e)}")
            return {"success": False, "error": str(e)}

# Global orchestrator instance
startup_evaluator = StartupEvaluationOrchestrator()
