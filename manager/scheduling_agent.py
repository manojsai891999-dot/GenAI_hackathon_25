"""
Scheduling Agent - Python Implementation
AI agent for coordinating meetings and communications with startup founders
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.cloud import firestore
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from vertexai.generative_models import GenerativeModel
import vertexai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeetingStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class MeetingRequest:
    startup_id: str
    founder_email: str
    founder_name: str
    meeting_type: str
    duration_minutes: int
    preferred_times: List[datetime]
    timezone: str = "UTC"

@dataclass
class ScheduledMeeting:
    meeting_id: str
    startup_id: str
    founder_email: str
    scheduled_time: datetime
    duration_minutes: int
    meeting_link: str
    status: MeetingStatus
    created_at: datetime

class StartupSchedulingAgent:
    """AI agent for scheduling and coordinating founder meetings"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-pro")
        
        # Initialize Firestore
        self.db = firestore.Client()
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "your-email@company.com"  # Configure this
        self.email_password = "your-app-password"   # Configure this
        
        # Business hours configuration
        self.business_hours = {
            "start": 9,  # 9 AM
            "end": 18,   # 6 PM
            "timezone": "UTC"
        }
        
        # Meeting templates
        self.email_templates = {
            "initial_outreach": {
                "subject": "Investment Evaluation Discussion - {startup_name}",
                "body": """Dear {founder_name},

We are currently evaluating {startup_name} for potential investment opportunities. Based on our initial analysis, we would like to schedule a brief discussion to learn more about your vision and progress.

Would you be available for a {duration}-minute video call in the coming week? We are flexible with timing and can accommodate your schedule.

Please let us know your availability, and we'll send you a calendar invitation with the meeting details.

Best regards,
Investment Evaluation Team

---
This is an automated message from our AI scheduling system. Please reply with your preferred meeting times."""
            },
            "meeting_confirmation": {
                "subject": "Meeting Confirmed - {meeting_date} at {meeting_time}",
                "body": """Hi {founder_name},

This confirms our meeting scheduled for {meeting_date} at {meeting_time} {timezone}.

Meeting Details:
• Duration: {duration} minutes
• Platform: Video Conference
• Meeting Link: {meeting_link}
• Meeting ID: {meeting_id}

We look forward to speaking with you about {startup_name}.

If you need to reschedule, please reply to this email at least 2 hours before the meeting time.

Best regards,
Investment Team"""
            },
            "reminder_24h": {
                "subject": "Reminder: Meeting Tomorrow - {startup_name}",
                "body": """Hi {founder_name},

This is a friendly reminder about our meeting tomorrow:

📅 Date: {meeting_date}
🕐 Time: {meeting_time} {timezone}
🔗 Link: {meeting_link}

Please join the meeting 5 minutes early to test your audio and video.

If you need to reschedule, please let us know as soon as possible.

Looking forward to our conversation!

Best regards,
Investment Team"""
            }
        }
    
    async def schedule_meeting(self, request: MeetingRequest) -> ScheduledMeeting:
        """Main method to schedule a meeting with a founder"""
        logger.info(f"Starting scheduling process for {request.founder_email}")
        
        try:
            # Step 1: Generate meeting ID
            meeting_id = f"meeting_{request.startup_id}_{int(datetime.utcnow().timestamp())}"
            
            # Step 2: Find optimal meeting time
            optimal_time = await self._find_optimal_time(request.preferred_times)
            
            # Step 3: Create meeting link
            meeting_link = await self._create_meeting_link(meeting_id, optimal_time, request.duration_minutes)
            
            # Step 4: Send initial outreach email
            await self._send_initial_outreach(request, meeting_id)
            
            # Step 5: Create meeting record
            meeting = ScheduledMeeting(
                meeting_id=meeting_id,
                startup_id=request.startup_id,
                founder_email=request.founder_email,
                scheduled_time=optimal_time,
                duration_minutes=request.duration_minutes,
                meeting_link=meeting_link,
                status=MeetingStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            # Step 6: Save to database
            await self._save_meeting(meeting)
            
            # Step 7: Schedule automated reminders
            await self._schedule_reminders(meeting)
            
            logger.info(f"Meeting scheduled successfully: {meeting_id}")
            return meeting
            
        except Exception as e:
            logger.error(f"Failed to schedule meeting: {str(e)}")
            raise
    
    async def _find_optimal_time(self, preferred_times: List[datetime]) -> datetime:
        """Find the optimal meeting time from preferred options"""
        
        # Filter times within business hours
        business_times = []
        for time in preferred_times:
            if self.business_hours["start"] <= time.hour <= self.business_hours["end"]:
                business_times.append(time)
        
        if business_times:
            # Return the earliest available business hour time
            return min(business_times)
        elif preferred_times:
            # Return the earliest preferred time if no business hours match
            return min(preferred_times)
        else:
            # Default to next business day at 10 AM
            tomorrow = datetime.utcnow() + timedelta(days=1)
            return tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    async def _create_meeting_link(self, meeting_id: str, meeting_time: datetime, duration: int) -> str:
        """Create a video meeting link (placeholder - integrate with actual service)"""
        
        # This is a placeholder - integrate with Google Meet, Zoom, or similar
        # For now, return a placeholder link
        base_url = "https://meet.google.com"
        meeting_code = f"eval-{meeting_id[-8:]}"
        
        return f"{base_url}/{meeting_code}"
    
    async def _send_initial_outreach(self, request: MeetingRequest, meeting_id: str):
        """Send initial outreach email to founder"""
        
        # Get startup information
        startup_doc = self.db.collection('startups').document(request.startup_id).get()
        startup_name = "your startup"
        
        if startup_doc.exists:
            startup_data = startup_doc.to_dict()
            startup_name = startup_data.get('name', startup_name)
        
        # Generate personalized email content
        email_content = await self._generate_personalized_email(request, startup_name)
        
        # Send email
        await self._send_email(
            to_email=request.founder_email,
            subject=self.email_templates["initial_outreach"]["subject"].format(startup_name=startup_name),
            body=email_content,
            meeting_id=meeting_id
        )
    
    async def _generate_personalized_email(self, request: MeetingRequest, startup_name: str) -> str:
        """Generate personalized email content using AI"""
        
        prompt = f"""
        Generate a personalized, professional email for scheduling an investment evaluation meeting.
        
        Context:
        - Startup name: {startup_name}
        - Founder name: {request.founder_name}
        - Meeting type: {request.meeting_type}
        - Duration: {request.duration_minutes} minutes
        
        The email should:
        1. Be warm but professional
        2. Explain the purpose (investment evaluation)
        3. Request availability for the meeting
        4. Be concise and respectful of their time
        5. Include next steps
        
        Keep it under 150 words and maintain a friendly, professional tone.
        """
        
        response = await self.model.generate_content_async(prompt)
        return response.text
    
    async def _send_email(self, to_email: str, subject: str, body: str, meeting_id: str):
        """Send email using SMTP"""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add meeting ID to headers for tracking
            msg['X-Meeting-ID'] = meeting_id
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            
            # Log email in database
            await self._log_email(meeting_id, to_email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise
    
    async def _log_email(self, meeting_id: str, to_email: str, subject: str, body: str):
        """Log email communication in database"""
        
        email_log = {
            'meeting_id': meeting_id,
            'to_email': to_email,
            'subject': subject,
            'body': body,
            'sent_at': datetime.utcnow(),
            'type': 'outbound'
        }
        
        self.db.collection('email_logs').add(email_log)
    
    async def _save_meeting(self, meeting: ScheduledMeeting):
        """Save meeting details to database"""
        
        meeting_data = {
            'meeting_id': meeting.meeting_id,
            'startup_id': meeting.startup_id,
            'founder_email': meeting.founder_email,
            'scheduled_time': meeting.scheduled_time,
            'duration_minutes': meeting.duration_minutes,
            'meeting_link': meeting.meeting_link,
            'status': meeting.status.value,
            'created_at': meeting.created_at,
            'updated_at': datetime.utcnow()
        }
        
        self.db.collection('meetings').document(meeting.meeting_id).set(meeting_data)
        logger.info(f"Meeting saved to database: {meeting.meeting_id}")
    
    async def _schedule_reminders(self, meeting: ScheduledMeeting):
        """Schedule automated reminder emails"""
        
        # Schedule 24-hour reminder
        reminder_time = meeting.scheduled_time - timedelta(hours=24)
        
        if reminder_time > datetime.utcnow():
            # In a real implementation, you would use a task queue like Cloud Tasks
            # For now, we'll just log the reminder schedule
            reminder_data = {
                'meeting_id': meeting.meeting_id,
                'reminder_type': '24h_before',
                'scheduled_for': reminder_time,
                'status': 'scheduled',
                'created_at': datetime.utcnow()
            }
            
            self.db.collection('reminders').add(reminder_data)
            logger.info(f"24h reminder scheduled for meeting {meeting.meeting_id}")
    
    async def process_email_response(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming email responses from founders"""
        
        try:
            # Extract meeting ID from email headers or subject
            meeting_id = email_data.get('meeting_id')
            sender_email = email_data.get('from_email')
            email_body = email_data.get('body', '')
            
            # Use AI to analyze the email response
            analysis = await self._analyze_email_response(email_body)
            
            if analysis.get('contains_availability'):
                # Extract proposed times
                proposed_times = analysis.get('proposed_times', [])
                
                # Update meeting status
                await self._update_meeting_status(meeting_id, MeetingStatus.CONFIRMED)
                
                # Send confirmation email
                await self._send_confirmation_email(meeting_id, proposed_times[0] if proposed_times else None)
                
                return {"status": "confirmed", "meeting_id": meeting_id}
            
            elif analysis.get('is_decline'):
                # Handle decline
                await self._update_meeting_status(meeting_id, MeetingStatus.CANCELLED)
                return {"status": "declined", "meeting_id": meeting_id}
            
            else:
                # Request clarification
                await self._request_clarification(meeting_id, sender_email)
                return {"status": "clarification_needed", "meeting_id": meeting_id}
                
        except Exception as e:
            logger.error(f"Failed to process email response: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_email_response(self, email_body: str) -> Dict[str, Any]:
        """Analyze email response using AI"""
        
        prompt = f"""
        Analyze this email response for meeting scheduling:
        
        Email: {email_body}
        
        Determine:
        1. Does it contain availability/acceptance? (true/false)
        2. Does it decline the meeting? (true/false)
        3. Are there specific times mentioned?
        4. What is the overall sentiment?
        
        Return as JSON:
        {{
            "contains_availability": true/false,
            "is_decline": true/false,
            "proposed_times": ["time1", "time2"],
            "sentiment": "positive/neutral/negative",
            "needs_clarification": true/false
        }}
        """
        
        response = await self.model.generate_content_async(prompt)
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"contains_availability": False, "is_decline": False, "needs_clarification": True}
    
    async def _update_meeting_status(self, meeting_id: str, status: MeetingStatus):
        """Update meeting status in database"""
        
        meeting_ref = self.db.collection('meetings').document(meeting_id)
        meeting_ref.update({
            'status': status.value,
            'updated_at': datetime.utcnow()
        })
        
        logger.info(f"Meeting {meeting_id} status updated to {status.value}")
    
    async def _send_confirmation_email(self, meeting_id: str, confirmed_time: Optional[datetime] = None):
        """Send meeting confirmation email"""
        
        # Get meeting details
        meeting_doc = self.db.collection('meetings').document(meeting_id).get()
        
        if not meeting_doc.exists:
            logger.error(f"Meeting {meeting_id} not found")
            return
        
        meeting_data = meeting_doc.to_dict()
        
        # Use confirmed time or original scheduled time
        meeting_time = confirmed_time or meeting_data['scheduled_time']
        
        # Format email content
        subject = self.email_templates["meeting_confirmation"]["subject"].format(
            meeting_date=meeting_time.strftime("%B %d, %Y"),
            meeting_time=meeting_time.strftime("%I:%M %p")
        )
        
        body = self.email_templates["meeting_confirmation"]["body"].format(
            founder_name=meeting_data.get('founder_name', 'there'),
            meeting_date=meeting_time.strftime("%B %d, %Y"),
            meeting_time=meeting_time.strftime("%I:%M %p"),
            timezone="UTC",
            duration=meeting_data['duration_minutes'],
            meeting_link=meeting_data['meeting_link'],
            meeting_id=meeting_id,
            startup_name=meeting_data.get('startup_name', 'your startup')
        )
        
        await self._send_email(
            to_email=meeting_data['founder_email'],
            subject=subject,
            body=body,
            meeting_id=meeting_id
        )
    
    async def _request_clarification(self, meeting_id: str, founder_email: str):
        """Request clarification from founder"""
        
        clarification_email = """
        Thank you for your response. To better assist you with scheduling, could you please provide:
        
        1. Your preferred meeting times (please include timezone)
        2. Any specific requirements or constraints
        
        We're flexible and want to find a time that works best for you.
        
        Best regards,
        Investment Team
        """
        
        await self._send_email(
            to_email=founder_email,
            subject="Clarification Needed - Meeting Scheduling",
            body=clarification_email,
            meeting_id=meeting_id
        )

# Usage example
async def main():
    """Example usage of the scheduling agent"""
    
    agent = StartupSchedulingAgent(project_id="your-project-id")
    
    # Example meeting request
    request = MeetingRequest(
        startup_id="startup-123",
        founder_email="founder@startup.com",
        founder_name="John Doe",
        meeting_type="initial_evaluation",
        duration_minutes=60,
        preferred_times=[
            datetime.utcnow() + timedelta(days=1, hours=2),
            datetime.utcnow() + timedelta(days=2, hours=3)
        ]
    )
    
    meeting = await agent.schedule_meeting(request)
    print(f"Meeting scheduled: {meeting.meeting_id}")

if __name__ == "__main__":
    asyncio.run(main())
