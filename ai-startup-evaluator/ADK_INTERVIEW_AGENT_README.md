# AI Interview Agent for Startup Founder Evaluation

## Overview

This implementation provides a comprehensive AI Interview Agent using Google Agent Development Kit (ADK) that conducts investment-focused interviews with startup founders. The system integrates with CloudSQL for data storage and Google Cloud Storage (GCS) for report generation.

## Features

### 🤖 AI Interview Agent
- **Google ADK Integration**: Built using Google Agent Development Kit for advanced conversational AI
- **Predefined Questions**: 6 core investment-related questions covering problem, customers, traction, business model, competition, and fundraising
- **Dynamic Follow-ups**: Intelligent follow-up questions based on founder responses
- **Real-time Analysis**: Sentiment analysis, confidence scoring, and insight extraction

### 💾 Data Storage
- **CloudSQL Integration**: All responses stored in structured database tables
- **Session Management**: Complete interview session tracking
- **Response Analysis**: Detailed analysis of each response with insights, red flags, and positive signals

### ☁️ Cloud Storage
- **GCS Integration**: Summary reports saved to Google Cloud Storage
- **Multiple Formats**: JSON and text report formats
- **Structured Naming**: Reports saved with founder name, session ID, and timestamp

### 📊 Report Generation
- **Comprehensive Analysis**: Key insights, risks, opportunities, and competitive landscape
- **Fundraising Details**: Funding goals, use of funds, and readiness assessment
- **Investment Recommendation**: AI-generated recommendation based on analysis
- **Next Steps**: Actionable next steps for further evaluation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │  ADK Interview   │    │   CloudSQL      │
│                 │◄──►│     Agent        │◄──►│   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Google Cloud    │
                       │ Storage (GCS)   │
                       └─────────────────┘
```

## Database Schema

### InterviewSession Table
- `session_id`: Unique session identifier
- `founder_name`: Name of the founder being interviewed
- `startup_name`: Name of the startup
- `session_status`: Active, completed, or abandoned
- `total_questions`: Total number of questions in the interview
- `questions_answered`: Number of questions answered
- `session_start_time`: When the session started
- `session_end_time`: When the session ended
- `duration_minutes`: Total interview duration
- `overall_sentiment`: Average sentiment score
- `overall_confidence`: Average confidence score
- `key_insights`: JSON array of key insights
- `red_flags`: JSON array of red flags
- `positive_signals`: JSON array of positive signals
- `summary_report_gcs_path`: Path to summary report in GCS

### InterviewResponse Table
- `session_id`: Links to interview session
- `founder_name`: Name of the founder
- `question`: The question asked
- `response`: The founder's response
- `question_category`: Category of the question (problem, customers, etc.)
- `response_timestamp`: When the response was given
- `sentiment_score`: Sentiment analysis score (-1 to 1)
- `confidence_score`: Confidence in the response (0 to 1)
- `key_insights`: JSON array of insights from the response
- `red_flags`: JSON array of red flags identified
- `positive_signals`: JSON array of positive signals identified

## Installation & Setup

### Prerequisites
- Python 3.8+
- Google Cloud Platform account
- CloudSQL instance
- GCS bucket
- Google ADK access

### 1. Install Dependencies

```bash
cd ai-startup-evaluator/backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database
# For local development: sqlite:///./startup_evaluator.db

# Google Cloud Configuration
GCS_BUCKET_NAME=your-gcs-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Optional: Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

### 3. Database Setup

```bash
# Create database tables
python -c "from backend.models.database import create_tables; create_tables()"
```

### 4. GCS Bucket Setup

```bash
# Create GCS bucket for reports
gsutil mb gs://your-gcs-bucket-name
```

## Usage

### 1. Command Line Testing

```bash
# Run the test suite
python test_adk_interview_agent.py
```

### 2. Web Interface

```bash
# Start the web interface
python web_interview_interface.py
```

Then open your browser to `http://localhost:5000`

### 3. Programmatic Usage

```python
from backend.agents.adk_interview_agent import interview_agent

# Start interview session
result = interview_agent.start_interview_session(
    founder_name="Sarah Johnson",
    startup_name="EcoTech Solutions"
)

# Process founder response
response_result = interview_agent.process_founder_response(
    session_data=result['session_data'],
    response="We're solving food waste in supply chains..."
)
```

## Interview Flow

### 1. Session Initialization
- Founder provides name and startup name
- System creates unique session ID
- Database session record created
- Greeting message generated

### 2. Question Sequence
1. **Problem Definition**: "What problem is your startup solving?"
2. **Target Customers**: "Who are your target customers?"
3. **Traction Metrics**: "What is your current traction (users, revenue, growth)?"
4. **Business Model**: "What is your business model?"
5. **Competition**: "Who are your competitors and how are you different?"
6. **Fundraising**: "What is your fundraising goal and how will you use the capital?"

### 3. Response Processing
- Real-time sentiment analysis
- Confidence scoring
- Insight extraction
- Red flag identification
- Positive signal detection

### 4. Follow-up Questions
- Dynamic follow-ups based on response quality
- Deeper probing when responses are brief
- Category-specific follow-up questions

### 5. Report Generation
- Comprehensive analysis of all responses
- Key insights aggregation
- Risk assessment
- Investment recommendation
- Next steps suggestions

## API Endpoints

### Web Interface Endpoints

- `POST /start_interview`: Start a new interview session
- `POST /send_response`: Process founder's response
- `GET /get_session_status/<session_id>`: Get session status
- `GET /end_session/<session_id>`: End interview session

### Request/Response Examples

#### Start Interview
```json
POST /start_interview
{
    "founder_name": "Sarah Johnson",
    "startup_name": "EcoTech Solutions"
}

Response:
{
    "status": "success",
    "session_id": "uuid-here",
    "greeting": "Hello Sarah! Thank you for...",
    "total_questions": 6
}
```

#### Send Response
```json
POST /send_response
{
    "session_id": "uuid-here",
    "response": "We're solving food waste in supply chains..."
}

Response:
{
    "status": "success",
    "interviewer_message": "Thank you for that response...",
    "analysis": {
        "sentiment_score": 0.8,
        "confidence_score": 0.9,
        "key_insights": ["Market size mentioned", "Problem urgency highlighted"],
        "red_flags": [],
        "positive_signals": ["Detailed response", "Data-driven approach"]
    },
    "progress": {
        "questions_answered": 1,
        "total_questions": 6,
        "progress_percentage": 16.7
    }
}
```

## Report Structure

### JSON Report Format
```json
{
    "interview_summary": {
        "founder_name": "Sarah Johnson",
        "startup_name": "EcoTech Solutions",
        "session_id": "uuid-here",
        "interview_date": "2024-01-15T10:30:00Z",
        "total_questions": 6,
        "duration_minutes": 30
    },
    "key_insights": {
        "strengths": ["Strong market validation", "Clear business model"],
        "risks": ["Limited traction data", "High competition"],
        "opportunities": ["Large addressable market", "Growing industry"],
        "competitive_landscape": {
            "analysis": "Competitive but differentiated...",
            "differentiation_mentioned": true,
            "competitive_advantage_clear": true
        }
    },
    "fundraising_details": {
        "funding_goal": "$8M",
        "use_of_funds": "40% sales, 30% product, 20% team, 10% working capital",
        "funding_timeline": "18 months",
        "funding_readiness": "High"
    },
    "overall_assessment": {
        "sentiment_score": 0.75,
        "confidence_score": 0.85,
        "recommendation": "Strong candidate - proceed to next stage",
        "next_steps": [
            "Schedule detailed due diligence meeting",
            "Review financial projections",
            "Conduct reference checks"
        ]
    },
    "detailed_responses": [
        {
            "question": "What problem is your startup solving?",
            "response": "We're solving food waste...",
            "category": "problem",
            "insights": ["Market size mentioned"],
            "sentiment": 0.8,
            "confidence": 0.9
        }
    ]
}
```

## Configuration Options

### Interview Questions
The predefined questions can be customized in `backend/agents/adk_interview_agent.py`:

```python
INVESTMENT_QUESTIONS = [
    {
        "question": "Your custom question here",
        "category": "custom_category",
        "follow_up_questions": [
            "Follow-up question 1",
            "Follow-up question 2"
        ]
    }
]
```

### Analysis Parameters
Sentiment and confidence scoring can be adjusted:

```python
def _calculate_sentiment(self, response: str) -> float:
    # Customize sentiment calculation logic
    pass

def _calculate_confidence(self, response: str) -> float:
    # Customize confidence calculation logic
    pass
```

## Monitoring & Analytics

### Database Queries
```sql
-- Get all completed interviews
SELECT * FROM interview_sessions WHERE session_status = 'completed';

-- Get average sentiment by founder
SELECT founder_name, AVG(overall_sentiment) as avg_sentiment
FROM interview_sessions
GROUP BY founder_name;

-- Get most common red flags
SELECT unnest(red_flags) as red_flag, COUNT(*) as frequency
FROM interview_sessions
WHERE red_flags IS NOT NULL
GROUP BY red_flag
ORDER BY frequency DESC;
```

### GCS Report Access
Reports are stored in GCS with the naming convention:
```
reports/{founder_name}_{session_id}_{timestamp}.json
reports/{founder_name}_{session_id}_{timestamp}.txt
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL in .env file
   - Ensure CloudSQL instance is running
   - Verify network connectivity

2. **GCS Upload Error**
   - Check GCS_BUCKET_NAME in .env file
   - Verify service account permissions
   - Ensure bucket exists

3. **ADK Agent Error**
   - Check Google ADK installation
   - Verify API credentials
   - Check model availability

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- Store sensitive credentials in environment variables
- Use IAM roles for GCS access
- Implement proper session management
- Add input validation and sanitization
- Consider rate limiting for API endpoints

## Performance Optimization

- Use connection pooling for database connections
- Implement caching for frequently accessed data
- Optimize GCS upload operations
- Consider async processing for report generation

## Future Enhancements

- Multi-language support
- Voice input/output integration
- Advanced analytics dashboard
- Integration with CRM systems
- Automated follow-up scheduling
- Machine learning model improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For questions or issues, please:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue in the repository
4. Contact the development team