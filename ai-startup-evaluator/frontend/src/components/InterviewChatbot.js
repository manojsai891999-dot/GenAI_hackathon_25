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
} from '@mui/icons-material';

const InterviewChatbot = ({ startupId, onInterviewComplete }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState('idle'); // idle, active, completed
  const [founderName, setFounderName] = useState('');
  const [startupName, setStartupName] = useState('');
  const [showStartDialog, setShowStartDialog] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startInterview = async () => {
    if (!founderName.trim()) {
      setError('Please enter the founder name');
      return;
    }

    setIsLoading(true);
    setError(null);
    setShowStartDialog(false);

    try {
      // Call the deployed ADK Interview Agent on Agent Engine
      const response = await fetch('/api/agent/start-interview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          founder_name: founderName,
          startup_name: startupName || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start interview session');
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        setSessionId(data.session_id);
        setSessionStatus('active');
        setMessages([{
          id: Date.now(),
          type: 'agent',
          content: data.greeting_message || "Hello! I'm your AI Interview Agent. I'll be conducting an investment-focused interview with you today. Let's start with the first question: What problem is your startup solving?",
          timestamp: new Date(),
        }]);
      } else {
        throw new Error(data.error_message || 'Failed to start interview');
      }
    } catch (err) {
      setError(err.message);
      setShowStartDialog(true);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Call the deployed ADK Interview Agent
      const response = await fetch('/api/agent/process-response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          response: inputMessage,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to process response');
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        const agentMessage = {
          id: Date.now() + 1,
          type: 'agent',
          content: data.next_message,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, agentMessage]);

        // Update analysis if available
        if (data.analysis) {
          setAnalysis(data.analysis);
        }

        // Check if interview is completed
        if (data.interview_completed) {
          setSessionStatus('completed');
          if (onInterviewComplete) {
            onInterviewComplete({
              sessionId,
              founderName,
              startupName,
              messages,
              analysis: data.analysis,
              summaryReport: data.summary_report,
            });
          }
        }
      } else {
        throw new Error(data.error_message || 'Failed to process response');
      }
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'system',
        content: `Error: ${err.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetInterview = () => {
    setMessages([]);
    setSessionId(null);
    setSessionStatus('idle');
    setAnalysis(null);
    setError(null);
    setShowStartDialog(true);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getSentimentIcon = (score) => {
    if (score > 0.3) return <TrendingUp sx={{ color: 'success.main' }} />;
    if (score < -0.3) return <TrendingDown sx={{ color: 'error.main' }} />;
    return <Assessment sx={{ color: 'warning.main' }} />;
  };

  const getSentimentColor = (score) => {
    if (score > 0.3) return 'success';
    if (score < -0.3) return 'error';
    return 'warning';
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <SmartToy />
            </Avatar>
            <Box>
              <Typography variant="h6">AI Interview Agent</Typography>
              <Typography variant="body2" color="text.secondary">
                {sessionStatus === 'idle' && 'Ready to start interview'}
                {sessionStatus === 'active' && 'Interview in progress'}
                {sessionStatus === 'completed' && 'Interview completed'}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            {sessionStatus === 'active' && (
              <Chip
                label="Live"
                color="success"
                size="small"
                icon={<PlayArrow />}
              />
            )}
            {sessionStatus === 'completed' && (
              <Chip
                label="Completed"
                color="primary"
                size="small"
                icon={<CheckCircle />}
              />
            )}
            <IconButton onClick={resetInterview} size="small">
              <Refresh />
            </IconButton>
          </Box>
        </Box>
      </Box>

      {/* Analysis Panel */}
      {analysis && (
        <Paper sx={{ p: 2, m: 2, bgcolor: 'background.default' }}>
          <Typography variant="subtitle2" gutterBottom>
            Real-time Analysis
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Chip
              icon={getSentimentIcon(analysis.sentiment_score)}
              label={`Sentiment: ${(analysis.sentiment_score * 100).toFixed(0)}%`}
              color={getSentimentColor(analysis.sentiment_score)}
              size="small"
            />
            <Chip
              label={`Confidence: ${(analysis.confidence_score * 100).toFixed(0)}%`}
              color="primary"
              size="small"
            />
            {analysis.key_insights && analysis.key_insights.length > 0 && (
              <Chip
                label={`${analysis.key_insights.length} insights`}
                color="info"
                size="small"
              />
            )}
            {analysis.red_flags && analysis.red_flags.length > 0 && (
              <Chip
                label={`${analysis.red_flags.length} red flags`}
                color="error"
                size="small"
                icon={<Warning />}
              />
            )}
          </Box>
        </Paper>
      )}

      {/* Messages */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
        {messages.length === 0 && sessionStatus === 'idle' && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Welcome to the AI Interview
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Click "Start Interview" to begin your investment evaluation session
            </Typography>
          </Box>
        )}

        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 1,
                maxWidth: '70%',
                flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
              }}
            >
              <Avatar
                sx={{
                  bgcolor: message.type === 'user' ? 'primary.main' : 'secondary.main',
                  width: 32,
                  height: 32,
                }}
              >
                {message.type === 'user' ? <Person /> : <SmartToy />}
              </Avatar>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: message.type === 'user' ? 'primary.main' : 'background.paper',
                  color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
                  borderRadius: 2,
                }}
              >
                <Typography variant="body1">{message.content}</Typography>
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    opacity: 0.7,
                    textAlign: 'right',
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          </Box>
        ))}

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                <SmartToy />
              </Avatar>
              <Paper sx={{ p: 2, borderRadius: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={16} />
                  <Typography variant="body2">AI is analyzing your response...</Typography>
                </Box>
              </Paper>
            </Box>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ m: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Input Area */}
      {sessionStatus === 'active' && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Type your response here..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              variant="outlined"
              size="small"
            />
            <Button
              variant="contained"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{ minWidth: 'auto', px: 2 }}
            >
              <Send />
            </Button>
          </Box>
        </Box>
      )}

      {/* Start Interview Dialog */}
      <Dialog open={showStartDialog} onClose={() => {}} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SmartToy color="primary" />
            Start AI Interview Session
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            The AI Interview Agent will conduct a comprehensive investment evaluation 
            covering key areas like problem definition, market opportunity, business model, 
            and competitive positioning.
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Founder Name *</InputLabel>
            <TextField
              value={founderName}
              onChange={(e) => setFounderName(e.target.value)}
              placeholder="Enter founder's full name"
              variant="outlined"
              fullWidth
            />
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Startup Name</InputLabel>
            <TextField
              value={startupName}
              onChange={(e) => setStartupName(e.target.value)}
              placeholder="Enter startup name (optional)"
              variant="outlined"
              fullWidth
            />
          </FormControl>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Interview Process:</strong>
              <br />• 6 core investment questions
              <br />• Real-time sentiment analysis
              <br />• Dynamic follow-up questions
              <br />• Comprehensive evaluation report
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={resetInterview} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={startInterview}
            variant="contained"
            disabled={!founderName.trim() || isLoading}
            startIcon={isLoading ? <CircularProgress size={16} /> : <PlayArrow />}
          >
            {isLoading ? 'Starting...' : 'Start Interview'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InterviewChatbot;