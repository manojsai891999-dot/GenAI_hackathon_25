# Google Calendar Integration Setup

The MeetingSchedulerAgent integrates with Google Calendar to automatically schedule meetings based on investment evaluation outcomes. Follow these steps to set up the integration.

## Prerequisites

- Google Cloud Project with Calendar API enabled
- Google Calendar account for the investment team
- Python environment with required dependencies installed

## Setup Steps

### 1. Enable Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Google Calendar API" and enable it

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop application" as the application type
4. Name it "AI Startup Evaluator - Calendar Integration"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the backend directory

### 3. Configure Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Google Calendar Integration
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=token.json
```

### 4. First-Time Authentication

When you first run the MeetingSchedulerAgent, it will:

1. Open a browser window for Google OAuth authentication
2. Ask you to sign in with your Google account
3. Request permission to access your calendar
4. Save the authentication token to `token.json` for future use

### 5. Calendar Configuration

The agent will use the primary calendar by default. You can:

- Create a dedicated "Investment Meetings" calendar
- Share it with team members who need access
- Update the `calendar_id` parameter in the agent if using a custom calendar

## Meeting Types and Scheduling Logic

The agent automatically determines meeting types based on evaluation results:

### High Priority (Schedule within 3 days)
- **Investment Committee Presentation** (90 minutes)
  - For startups with "pass" recommendation and score ≥ 7
  - Includes partners, senior associates, and analysts

### Medium Priority (Schedule within 7 days)
- **Due Diligence Deep Dive** (60 minutes)
  - For "maybe" recommendations or scores 5-7
  - Includes partners and analysts
- **Founder Interview** (45 minutes)
  - For promising opportunities needing founder assessment
  - Includes partners

### Low Priority (Schedule within 14 days)
- **Initial Screening Call** (30 minutes)
  - For early-stage evaluations
  - Basic investor screening

## Features

### Automatic Scheduling
- Checks calendar availability across business hours
- Avoids weekends and conflicts
- Suggests alternative time slots
- Creates detailed calendar events with context

### Meeting Preparation
- Includes investment memo and key data in event description
- Sets up email reminders (24 hours and 30 minutes before)
- Prepares attendee list based on meeting type
- Links to relevant documents and materials

### Integration with Workflow
- Receives input from MemoAgent with evaluation results
- Schedules meetings before VoiceInterviewAgent interviews
- Passes meeting details to subsequent workflow steps

## Customization

### Business Hours
Default business hours are 9 AM to 5 PM, Monday-Friday. You can modify this in the `find_available_slots` function:

```python
start_hour = 9  # Change start time
end_hour = 17   # Change end time
```

### Attendee Lists
Update the `determine_attendees` function to match your team structure:

```python
def determine_attendees(meeting_type: str, evaluation_data: dict) -> List[str]:
    base_attendees = ["your-email@firm.com"]  # Update with actual emails
    # ... rest of the logic
```

### Meeting Duration
Adjust meeting durations in the `determine_meeting_type` function based on your preferences.

## Troubleshooting

### Authentication Issues
- Ensure `credentials.json` is in the correct location
- Check that the Google Calendar API is enabled
- Verify OAuth consent screen is configured

### Calendar Access
- Make sure the authenticated account has access to the target calendar
- Check calendar sharing permissions for team members

### Time Zone Issues
- The agent uses UTC by default
- Update the `timeZone` parameter in calendar events if needed

## Security Considerations

- Keep `credentials.json` and `token.json` secure and out of version control
- Add them to `.gitignore`
- Use service accounts for production deployments
- Regularly rotate OAuth tokens

## Testing

Test the integration by:

1. Running the agent with sample evaluation data
2. Checking that calendar events are created correctly
3. Verifying attendee invitations are sent
4. Confirming meeting details and preparation materials

## Support

For issues with the Google Calendar integration:
- Check the Google Calendar API documentation
- Review the agent logs for error messages
- Ensure all dependencies are installed correctly
- Verify API quotas and limits are not exceeded
