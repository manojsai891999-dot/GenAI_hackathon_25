import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Grid,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  PlayArrow,
  Stop,
  Refresh,
  Assessment,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Close,
  Business,
  PersonPin,
  Psychology,
  Analytics,
} from '@mui/icons-material';
import InterviewChatbot from '../components/InterviewChatbot';

const InterviewChat = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [interviewData, setInterviewData] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const steps = [
    'Start Interview',
    'Conduct Interview',
    'Review Results',
    'Generate Report'
  ];

  const handleInterviewComplete = (data) => {
    setInterviewData(data);
    setCurrentStep(2);
    setShowResults(true);
  };

  const handleGenerateReport = () => {
    setCurrentStep(3);
    // Here you would typically call an API to generate the final report
    console.log('Generating final report for:', interviewData);
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Typography variant="h4" gutterBottom>
          AI Interview Agent
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Conduct investment-focused interviews with startup founders using our AI-powered agent
        </Typography>
        
        {/* Progress Stepper */}
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Box>

      {/* Main Content */}
      <Box sx={{ flexGrow: 1, display: 'flex' }}>
        {/* Chat Interface */}
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <InterviewChatbot 
            onInterviewComplete={handleInterviewComplete}
          />
        </Box>

        {/* Sidebar with Information */}
        <Box sx={{ width: 350, borderLeft: 1, borderColor: 'divider', p: 2, bgcolor: 'background.default' }}>
          <Typography variant="h6" gutterBottom>
            Interview Guide
          </Typography>
          
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
                Investment Focus Areas
              </Typography>
              <List dense>
                <ListItem sx={{ pl: 0 }}>
                  <ListItemText 
                    primary="Problem & Solution"
                    secondary="Market need and product fit"
                  />
                </ListItem>
                <ListItem sx={{ pl: 0 }}>
                  <ListItemText 
                    primary="Target Customers"
                    secondary="Market size and segmentation"
                  />
                </ListItem>
                <ListItem sx={{ pl: 0 }}>
                  <ListItemText 
                    primary="Traction & Metrics"
                    secondary="Growth and performance data"
                  />
                </ListItem>
                <ListItem sx={{ pl: 0 }}>
                  <ListItemText 
                    primary="Business Model"
                    secondary="Revenue and monetization"
                  />
                </ListItem>
                <ListItem sx={{ pl: 0 }}>
                  <ListItemText 
                    primary="Competition"
                    secondary="Market positioning"
                  />
                </ListItem>
                <ListItem sx={{ pl: 0 }}>
                  <ListItemText 
                    primary="Fundraising"
                    secondary="Capital needs and use"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>

          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Analysis Features
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip
                  icon={<TrendingUp />}
                  label="Sentiment Analysis"
                  color="success"
                  size="small"
                />
                <Chip
                  icon={<Assessment />}
                  label="Confidence Scoring"
                  color="primary"
                  size="small"
                />
                <Chip
                  icon={<CheckCircle />}
                  label="Insight Extraction"
                  color="info"
                  size="small"
                />
                <Chip
                  icon={<Warning />}
                  label="Risk Assessment"
                  color="warning"
                  size="small"
                />
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                <Analytics sx={{ mr: 1, verticalAlign: 'middle' }} />
                Expected Duration
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • 6 core questions
                <br />
                • Dynamic follow-ups
                <br />
                • Real-time analysis
                <br />
                • 15-30 minutes total
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Results Dialog */}
      <Dialog 
        open={showResults} 
        onClose={() => setShowResults(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircle color="success" />
            Interview Completed Successfully
          </Box>
        </DialogTitle>
        <DialogContent>
          {interviewData && (
            <Box>
              <Typography variant="body1" gutterBottom>
                Interview session completed for <strong>{interviewData.founderName}</strong>
                {interviewData.startupName && ` at ${interviewData.startupName}`}.
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="h6" gutterBottom>
                Session Summary
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Session ID
                  </Typography>
                  <Typography variant="body2">
                    {interviewData.sessionId}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Messages Exchanged
                  </Typography>
                  <Typography variant="body2">
                    {interviewData.messages.length}
                  </Typography>
                </Grid>
              </Grid>

              {interviewData.analysis && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Analysis Results
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    <Chip
                      icon={<TrendingUp />}
                      label={`Sentiment: ${(interviewData.analysis.sentiment_score * 100).toFixed(0)}%`}
                      color={interviewData.analysis.sentiment_score > 0.3 ? 'success' : 'warning'}
                      size="small"
                    />
                    <Chip
                      label={`Confidence: ${(interviewData.analysis.confidence_score * 100).toFixed(0)}%`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                </Box>
              )}

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  A comprehensive evaluation report has been generated and stored in Google Cloud Storage.
                  The report includes detailed analysis, insights, and investment recommendations.
                </Typography>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowResults(false)}>
            Close
          </Button>
          <Button 
            variant="contained" 
            onClick={handleGenerateReport}
            startIcon={<Assessment />}
          >
            Generate Final Report
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InterviewChat;