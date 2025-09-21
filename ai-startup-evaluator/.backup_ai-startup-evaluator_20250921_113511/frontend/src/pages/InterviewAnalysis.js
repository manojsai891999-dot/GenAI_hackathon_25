import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore,
  Mic,
  QuestionAnswer,
  SentimentSatisfied,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  PlayArrow,
  GetApp,
  Assessment,
} from '@mui/icons-material';
import { apiEndpoints } from '../services/api';

const InterviewAnalysis = () => {
  const { id } = useParams();
  const [questionsDialogOpen, setQuestionsDialogOpen] = useState(false);

  // Fetch interview data
  const { data: interviewsData, isLoading: interviewsLoading, error: interviewsError } = useQuery(
    ['interviews', id],
    () => apiEndpoints.getInterviews(id),
    {
      select: (response) => response.data,
      enabled: !!id,
    }
  );

  // Fetch interview questions
  const { data: questionsData, isLoading: questionsLoading } = useQuery(
    ['interviewQuestions', id],
    () => apiEndpoints.getInterviewQuestions(id),
    {
      select: (response) => response.data.data,
      enabled: !!id,
    }
  );

  const getSentimentColor = (score) => {
    if (score > 0.3) return 'success.main';
    if (score < -0.3) return 'error.main';
    return 'warning.main';
  };

  const getSentimentIcon = (score) => {
    if (score > 0.3) return <TrendingUp sx={{ color: 'success.main' }} />;
    if (score < -0.3) return <TrendingDown sx={{ color: 'error.main' }} />;
    return <SentimentSatisfied sx={{ color: 'warning.main' }} />;
  };

  const getCoverageColor = (score) => {
    if (score >= 0.7) return 'success';
    if (score >= 0.4) return 'warning';
    return 'error';
  };

  if (interviewsError) {
    return (
      <Alert severity="error">
        Failed to load interview data. Please try again later.
      </Alert>
    );
  }

  if (interviewsLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Loading interview analysis...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">
          Interview Analysis
        </Typography>
        <Button
          variant="outlined"
          startIcon={<QuestionAnswer />}
          onClick={() => setQuestionsDialogOpen(true)}
          disabled={questionsLoading}
        >
          View Interview Questions
        </Button>
      </Box>

      {!interviewsData || interviewsData.length === 0 ? (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 3 }}>
              No interview data available for this startup. Upload a voice interview to see analysis here.
            </Alert>
          </Grid>

          {/* Interview Questions Preview */}
          {questionsData && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Structured Interview Framework
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Our AI agent uses a comprehensive set of {questionsData.total_questions} predefined questions 
                    across {questionsData.total_categories} categories to ensure thorough founder evaluation.
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    {questionsData.interview_script?.slice(0, 6).map((category, index) => (
                      <Chip
                        key={index}
                        label={category.category}
                        variant="outlined"
                        size="small"
                      />
                    ))}
                    {questionsData.interview_script?.length > 6 && (
                      <Chip
                        label={`+${questionsData.interview_script.length - 6} more`}
                        variant="outlined"
                        size="small"
                        color="primary"
                      />
                    )}
                  </Box>

                  <Typography variant="body2" color="text.secondary">
                    Estimated Duration: {questionsData.estimated_duration}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      ) : (
        <Grid container spacing={3}>
          {interviewsData.map((interview, index) => (
            <React.Fragment key={interview.id || index}>
              {/* Interview Overview */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          Interview #{index + 1}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {interview.interview_date 
                            ? new Date(interview.interview_date).toLocaleDateString()
                            : 'Date not available'
                          }
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip
                          label={interview.interview_type?.toUpperCase() || 'VOICE'}
                          color="primary"
                          size="small"
                          icon={<Mic />}
                        />
                        {interview.duration_minutes && (
                          <Chip
                            label={`${interview.duration_minutes} min`}
                            variant="outlined"
                            size="small"
                          />
                        )}
                      </Box>
                    </Box>

                    {/* Key Metrics */}
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      <Grid item xs={6} sm={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                            {getSentimentIcon(interview.sentiment_score || 0)}
                            <Typography variant="h6" sx={{ ml: 1 }}>
                              {((interview.sentiment_score || 0) * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            Sentiment Score
                          </Typography>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={6} sm={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h6" color="primary">
                            {((interview.confidence_score || 0) * 100).toFixed(0)}%
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Analysis Confidence
                          </Typography>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={6} sm={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h6" color="success.main">
                            {interview.positive_signals?.length || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Positive Signals
                          </Typography>
                        </Box>
                      </Grid>
                      
                      <Grid item xs={6} sm={3}>
                        <Box sx={{ textAlign: 'center' }}>
                          <Typography variant="h6" color="error.main">
                            {interview.red_flags?.length || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Red Flags
                          </Typography>
                        </Box>
                      </Grid>
                    </Grid>

                    {/* Interview Summary */}
                    {interview.transcript_summary && (
                      <Box sx={{ p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                        <Typography variant="body2">
                          {interview.transcript_summary}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Key Insights */}
              {interview.key_insights && interview.key_insights.length > 0 && (
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="primary">
                        Key Insights
                      </Typography>
                      <List dense>
                        {interview.key_insights.map((insight, idx) => (
                          <ListItem key={idx} sx={{ pl: 0 }}>
                            <ListItemIcon>
                              <Assessment sx={{ color: 'primary.main', fontSize: 20 }} />
                            </ListItemIcon>
                            <ListItemText primary={insight} />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Positive Signals & Red Flags */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="success.main">
                      Positive Signals
                    </Typography>
                    {interview.positive_signals && interview.positive_signals.length > 0 ? (
                      <List dense>
                        {interview.positive_signals.map((signal, idx) => (
                          <ListItem key={idx} sx={{ pl: 0 }}>
                            <ListItemIcon>
                              <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                            </ListItemIcon>
                            <ListItemText primary={signal} />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No specific positive signals identified.
                      </Typography>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="h6" gutterBottom color="error.main">
                      Red Flags
                    </Typography>
                    {interview.red_flags && interview.red_flags.length > 0 ? (
                      <List dense>
                        {interview.red_flags.map((flag, idx) => (
                          <ListItem key={idx} sx={{ pl: 0 }}>
                            <ListItemIcon>
                              <Warning sx={{ color: 'error.main', fontSize: 20 }} />
                            </ListItemIcon>
                            <ListItemText primary={flag} />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No red flags identified.
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Audio Files Access */}
              {(interview.transcript_gcs_path || interview.audio_gcs_path) && (
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Interview Files
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        {interview.audio_gcs_path && (
                          <Button
                            variant="outlined"
                            startIcon={<PlayArrow />}
                            onClick={() => {
                              // This would open the audio file
                              console.log('Play audio:', interview.audio_gcs_path);
                            }}
                          >
                            Play Audio
                          </Button>
                        )}
                        {interview.transcript_gcs_path && (
                          <Button
                            variant="outlined"
                            startIcon={<GetApp />}
                            onClick={() => {
                              // This would download the transcript
                              console.log('Download transcript:', interview.transcript_gcs_path);
                            }}
                          >
                            Download Transcript
                          </Button>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </React.Fragment>
          ))}
        </Grid>
      )}

      {/* Interview Questions Dialog */}
      <Dialog
        open={questionsDialogOpen}
        onClose={() => setQuestionsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Structured Interview Questions
        </DialogTitle>
        <DialogContent>
          {questionsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : questionsData ? (
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {questionsData.total_questions} questions across {questionsData.total_categories} categories
                • Estimated Duration: {questionsData.estimated_duration}
              </Typography>

              {questionsData.interview_script?.map((category, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        {category.category}
                      </Typography>
                      <Chip
                        label={`${category.questions.length} questions`}
                        size="small"
                        color="primary"
                        sx={{ mr: 2 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {category.estimated_time}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List>
                      {category.questions.map((question, qIndex) => (
                        <ListItem key={qIndex} sx={{ pl: 0 }}>
                          <ListItemIcon>
                            <Typography variant="body2" color="primary" fontWeight="bold">
                              {qIndex + 1}.
                            </Typography>
                          </ListItemIcon>
                          <ListItemText primary={question} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          ) : (
            <Alert severity="error">
              Failed to load interview questions.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQuestionsDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InterviewAnalysis;
