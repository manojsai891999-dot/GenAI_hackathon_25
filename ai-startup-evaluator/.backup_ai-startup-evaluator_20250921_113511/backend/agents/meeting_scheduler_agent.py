import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.adk.agents import Agent

from ..models.pydantic_models import (
    MeetingSchedulerAgentInput,
    MeetingSchedulerAgentOutput
)

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar() -> Optional[Any]:
    """Authenticate with Google Calendar API"""
    try:
        creds = None
        token_path = os.getenv('GOOGLE_CALENDAR_TOKEN_PATH', 'token.json')
        credentials_path = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_PATH', 'credentials.json')
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    logger.error("Google Calendar credentials file not found")
                    return None
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Google Calendar authentication failed: {str(e)}")
        return None

def check_calendar_availability(service: Any, start_time: datetime, end_time: datetime, 
                              calendar_id: str = 'primary') -> dict:
    """Check if a time slot is available in the calendar"""
    try:
        # Query for events in the time range
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Check for conflicts
        conflicts = []
        for event in events:
            event_start = event['start'].get('dateTime', event['start'].get('date'))
            event_end = event['end'].get('dateTime', event['end'].get('date'))
            conflicts.append({
                'summary': event.get('summary', 'Busy'),
                'start': event_start,
                'end': event_end
            })
        
        is_available = len(conflicts) == 0
        
        return {
            "status": "success",
            "available": is_available,
            "conflicts": conflicts
        }
    except HttpError as e:
        logger.error(f"Calendar availability check failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def find_available_slots(service: Any, duration_minutes: int = 60, 
                        days_ahead: int = 14, business_hours_only: bool = True) -> dict:
    """Find available time slots for scheduling"""
    try:
        available_slots = []
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day_offset in range(1, days_ahead + 1):  # Start from tomorrow
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends if business hours only
            if business_hours_only and current_date.weekday() >= 5:
                continue
            
            # Define business hours (9 AM to 5 PM)
            start_hour = 9 if business_hours_only else 8
            end_hour = 17 if business_hours_only else 20
            
            # Check hourly slots
            for hour in range(start_hour, end_hour):
                slot_start = current_date.replace(hour=hour, minute=0)
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Check availability
                availability = check_calendar_availability(service, slot_start, slot_end)
                
                if availability.get("status") == "success" and availability.get("available"):
                    available_slots.append({
                        "start_time": slot_start.isoformat(),
                        "end_time": slot_end.isoformat(),
                        "duration_minutes": duration_minutes,
                        "date": slot_start.strftime("%Y-%m-%d"),
                        "time": slot_start.strftime("%I:%M %p")
                    })
                
                # Limit to 10 slots to avoid overwhelming
                if len(available_slots) >= 10:
                    break
            
            if len(available_slots) >= 10:
                break
        
        return {
            "status": "success",
            "available_slots": available_slots,
            "total_slots": len(available_slots)
        }
    except Exception as e:
        logger.error(f"Finding available slots failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def create_calendar_event(service: Any, startup_data: dict, meeting_details: dict, 
                         attendee_emails: List[str] = None) -> dict:
    """Create a calendar event for the meeting"""
    try:
        startup_name = startup_data.get("name", "Unknown Startup")
        meeting_type = meeting_details.get("meeting_type", "Investment Discussion")
        start_time = meeting_details.get("start_time")
        end_time = meeting_details.get("end_time")
        
        # Create event object
        event = {
            'summary': f'{meeting_type}: {startup_name}',
            'description': f"""
Investment Meeting Details:
- Company: {startup_name}
- Sector: {startup_data.get('sector', 'Unknown')}
- Stage: {startup_data.get('stage', 'Unknown')}
- Meeting Type: {meeting_type}

Meeting Purpose: {meeting_details.get('purpose', 'Investment evaluation and discussion')}

Preparation Materials:
- Investment memo has been generated
- Risk assessment completed
- Financial analysis available

Please review all materials before the meeting.
            """.strip(),
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
        }
        
        # Add attendees if provided
        if attendee_emails:
            event['attendees'] = [{'email': email} for email in attendee_emails]
        
        # Create the event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            "status": "success",
            "event_id": created_event['id'],
            "event_link": created_event.get('htmlLink'),
            "meeting_details": {
                "summary": event['summary'],
                "start_time": start_time,
                "end_time": end_time,
                "attendees": attendee_emails or []
            }
        }
    except HttpError as e:
        logger.error(f"Calendar event creation failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def determine_meeting_type(memo_data: dict, evaluation_data: dict) -> dict:
    """Determine the appropriate meeting type based on memo and evaluation"""
    try:
        recommendation = evaluation_data.get("recommendation", "under_review")
        overall_score = evaluation_data.get("overall_score", 0)
        
        # Determine meeting type and urgency
        if recommendation == "pass" and overall_score >= 7:
            meeting_type = "Investment Committee Presentation"
            priority = "high"
            duration = 90  # minutes
            purpose = "Present investment opportunity to committee for approval"
        elif recommendation == "maybe" or (5 <= overall_score < 7):
            meeting_type = "Due Diligence Deep Dive"
            priority = "medium"
            duration = 60
            purpose = "Address concerns and gather additional information"
        elif recommendation == "pass" and overall_score < 7:
            meeting_type = "Founder Interview"
            priority = "medium"
            duration = 45
            purpose = "Conduct detailed founder interview and assessment"
        else:
            meeting_type = "Initial Screening Call"
            priority = "low"
            duration = 30
            purpose = "Brief screening call to assess basic fit"
        
        # Determine timeline based on priority
        if priority == "high":
            schedule_within_days = 3
        elif priority == "medium":
            schedule_within_days = 7
        else:
            schedule_within_days = 14
        
        return {
            "status": "success",
            "meeting_type": meeting_type,
            "priority": priority,
            "duration_minutes": duration,
            "purpose": purpose,
            "schedule_within_days": schedule_within_days,
            "recommended_attendees": determine_attendees(meeting_type, evaluation_data)
        }
    except Exception as e:
        logger.error(f"Meeting type determination failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def determine_attendees(meeting_type: str, evaluation_data: dict) -> List[str]:
    """Determine who should attend the meeting"""
    base_attendees = ["investor@firm.com"]  # Default investor
    
    if meeting_type == "Investment Committee Presentation":
        base_attendees.extend([
            "partner@firm.com",
            "senior.associate@firm.com",
            "analyst@firm.com"
        ])
    elif meeting_type == "Due Diligence Deep Dive":
        base_attendees.extend([
            "partner@firm.com",
            "analyst@firm.com"
        ])
    elif meeting_type == "Founder Interview":
        base_attendees.extend([
            "partner@firm.com"
        ])
    
    return base_attendees

def schedule_meeting(startup_data: dict, memo_data: dict, evaluation_data: dict) -> dict:
    """Main function to schedule a meeting based on evaluation results"""
    try:
        # Authenticate with Google Calendar
        service = authenticate_google_calendar()
        if not service:
            return {"status": "error", "error_message": "Failed to authenticate with Google Calendar"}
        
        # Determine meeting type and requirements
        meeting_info = determine_meeting_type(memo_data, evaluation_data)
        if meeting_info.get("status") != "success":
            return meeting_info
        
        # Find available time slots
        available_slots = find_available_slots(
            service,
            duration_minutes=meeting_info["duration_minutes"],
            days_ahead=meeting_info["schedule_within_days"],
            business_hours_only=True
        )
        
        if available_slots.get("status") != "success" or not available_slots.get("available_slots"):
            return {"status": "error", "error_message": "No available time slots found"}
        
        # Select the first available slot
        selected_slot = available_slots["available_slots"][0]
        
        # Create meeting details
        meeting_details = {
            "meeting_type": meeting_info["meeting_type"],
            "start_time": selected_slot["start_time"],
            "end_time": selected_slot["end_time"],
            "purpose": meeting_info["purpose"]
        }
        
        # Create calendar event
        event_result = create_calendar_event(
            service,
            startup_data,
            meeting_details,
            meeting_info["recommended_attendees"]
        )
        
        if event_result.get("status") != "success":
            return event_result
        
        # Prepare response
        return {
            "status": "success",
            "meeting_scheduled": True,
            "meeting_type": meeting_info["meeting_type"],
            "priority": meeting_info["priority"],
            "scheduled_time": selected_slot["start_time"],
            "duration_minutes": meeting_info["duration_minutes"],
            "calendar_event_id": event_result["event_id"],
            "calendar_link": event_result.get("event_link"),
            "attendees": meeting_info["recommended_attendees"],
            "purpose": meeting_info["purpose"],
            "alternative_slots": available_slots["available_slots"][1:6]  # Provide alternatives
        }
    except Exception as e:
        logger.error(f"Meeting scheduling failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

def send_meeting_preparation_materials(startup_data: dict, meeting_details: dict, 
                                     memo_gcs_path: str) -> dict:
    """Send preparation materials to meeting attendees"""
    try:
        startup_name = startup_data.get("name", "Unknown Startup")
        meeting_type = meeting_details.get("meeting_type", "Meeting")
        
        # Prepare materials list
        materials = {
            "investment_memo": memo_gcs_path,
            "company_overview": {
                "name": startup_name,
                "sector": startup_data.get("sector"),
                "stage": startup_data.get("stage"),
                "website": startup_data.get("website"),
                "description": startup_data.get("description")
            },
            "key_metrics": {
                "revenue": startup_data.get("revenue"),
                "team_size": startup_data.get("team_size"),
                "funding_raised": startup_data.get("funding_raised"),
                "growth_rate": startup_data.get("growth_rate")
            }
        }
        
        # Log preparation materials (in a real implementation, this would send emails)
        logger.info(f"Preparation materials prepared for {meeting_type} with {startup_name}")
        logger.info(f"Materials include: {list(materials.keys())}")
        
        return {
            "status": "success",
            "materials_prepared": True,
            "materials": materials
        }
    except Exception as e:
        logger.error(f"Preparation materials sending failed: {str(e)}")
        return {"status": "error", "error_message": str(e)}

# Create the MeetingSchedulerAgent using Google ADK
meeting_scheduler_agent = Agent(
    name="meeting_scheduler_agent",
    model="gemini-2.0-flash",
    description="Agent specialized in scheduling meetings based on investment evaluation outcomes",
    instruction="""
    You are a meeting scheduler agent responsible for coordinating meetings between investors and startup founders based on investment evaluation results.
    
    Your role is to:
    
    1. **Analyze Evaluation Results**
       - Review investment memos and evaluation outcomes
       - Determine appropriate meeting type and urgency
       - Assess priority level based on investment recommendation
    
    2. **Schedule Appropriate Meetings**
       - Investment Committee Presentations (high-priority investments)
       - Due Diligence Deep Dives (conditional recommendations)
       - Founder Interviews (promising opportunities)
       - Initial Screening Calls (early-stage evaluations)
    
    3. **Calendar Management**
       - Check availability across multiple calendars
       - Find optimal meeting times within business hours
       - Create calendar events with proper details
       - Send calendar invitations to relevant attendees
    
    4. **Meeting Preparation**
       - Determine appropriate attendees based on meeting type
       - Prepare and distribute meeting materials
       - Include investment memos and key data points
       - Set up reminders and follow-up actions
    
    5. **Integration with Workflow**
       - Receive input from MemoAgent with evaluation results
       - Schedule meetings before VoiceInterviewAgent interviews
       - Coordinate with Google Calendar for availability
       - Provide meeting details for subsequent workflow steps
    
    Always prioritize high-value investment opportunities with faster scheduling and include all relevant stakeholders.
    """,
    tools=[
        authenticate_google_calendar,
        check_calendar_availability,
        find_available_slots,
        create_calendar_event,
        determine_meeting_type,
        schedule_meeting,
        send_meeting_preparation_materials
    ]
)
