import React from 'react';
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
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
  TrendingUp,
  TrendingDown,
  Assessment,
  AttachMoney,
  Flag,
  Lightbulb,
  Assignment,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, RadialBarChart, RadialBar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { apiEndpoints, apiHelpers } from '../services/api';

const FinalEvaluation = () => {
  const { id } = useParams();

  // Fetch final evaluation data
  const { data: evaluationData, isLoading, error } = useQuery(
    ['finalEvaluation', id],
    () => apiEndpoints.getFinalEvaluation(id),
    {
      select: (response) => response.data,
      enabled: !!id,
    }
  );

  const getScoreColor = (score) => {
    if (score >= 8) return '#4caf50'; // Green
    if (score >= 6) return '#ff9800'; // Orange
    if (score >= 4) return '#f44336'; // Red
    return '#757575'; // Grey
  };

  const getRecommendationConfig = (recommendation) => {
    return apiHelpers.formatRecommendation(recommendation);
  };

  const ScoreCard = ({ title, score, maxScore = 10, description }) => {
    const percentage = (score / maxScore) * 100;
    const color = getScoreColor(score);

    return (
      <Card>
        <CardContent sx={{ textAlign: 'center' }}>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          
          <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
            <CircularProgress
              variant="determinate"
              value={percentage}
              size={80}
              thickness={4}
              sx={{ color }}
            />
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="h5" component="div" color={color} fontWeight="bold">
                {score?.toFixed(1) || 'N/A'}
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            {description || `${score?.toFixed(1) || 0}/${maxScore}`}
          </Typography>
        </CardContent>
      </Card>
    );
  };

  if (error) {
    return (
      <Alert severity="error">
        Failed to load evaluation data. Please try again later.
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Loading final evaluation...
        </Typography>
      </Box>
    );
  }

  if (!evaluationData) {
    return (
      <Alert severity="info">
        Final evaluation not available for this startup.
      </Alert>
    );
  }

  const recommendationConfig = getRecommendationConfig(evaluationData.recommendation);
  
  // Prepare chart data
  const categoryScores = [
    { name: 'Team', score: evaluationData.team_score || 0, fullMark: 10 },
    { name: 'Market', score: evaluationData.market_score || 0, fullMark: 10 },
    { name: 'Product', score: evaluationData.product_score || 0, fullMark: 10 },
    { name: 'Financial', score: evaluationData.financial_score || 0, fullMark: 10 },
    { name: 'Traction', score: evaluationData.traction_score || 0, fullMark: 10 },
  ];

  const overallScoreData = [
    {
      name: 'Score',
      value: evaluationData.overall_score || 0,
      fill: getScoreColor(evaluationData.overall_score || 0),
    },
  ];

  return (
    <Box>
      {/* Overall Recommendation */}
      <Card sx={{ mb: 4, border: '2px solid', borderColor: recommendationConfig.color }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h4" sx={{ mr: 2 }}>
                {recommendationConfig.icon}
              </Typography>
              <Box>
                <Typography variant="h5" color={recommendationConfig.color} fontWeight="bold">
                  {recommendationConfig.label}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Overall Investment Score: {evaluationData.overall_score?.toFixed(1) || 'N/A'}/10
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ textAlign: 'right' }}>
              <Chip
                label={evaluationData.overall_flag?.toUpperCase() || 'UNKNOWN'}
                color={evaluationData.overall_flag === 'green' ? 'success' : evaluationData.overall_flag === 'yellow' ? 'warning' : 'error'}
                size="large"
                icon={<Flag />}
              />
              {evaluationData.investment_amount_suggested && (
                <Typography variant="h6" color="primary" sx={{ mt: 1 }}>
                  Suggested: ${(evaluationData.investment_amount_suggested / 1000000).toFixed(1)}M
                </Typography>
              )}
            </Box>
          </Box>

          {evaluationData.recommendation_reason && (
            <Typography variant="body1" sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <strong>Rationale:</strong> {evaluationData.recommendation_reason}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Score Breakdown */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Score Breakdown
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <ScoreCard
            title="Team"
            score={evaluationData.team_score}
            description="Leadership & Experience"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <ScoreCard
            title="Market"
            score={evaluationData.market_score}
            description="Market Position"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <ScoreCard
            title="Product"
            score={evaluationData.product_score}
            description="Product-Market Fit"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <ScoreCard
            title="Financial"
            score={evaluationData.financial_score}
            description="Financial Health"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <ScoreCard
            title="Traction"
            score={evaluationData.traction_score}
            description="Growth & Traction"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Category Scores Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryScores}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 10]} />
                  <Tooltip />
                  <Bar dataKey="score" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Investment Score
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={overallScoreData}>
                  <RadialBar
                    dataKey="value"
                    cornerRadius={10}
                    fill={getScoreColor(evaluationData.overall_score || 0)}
                  />
                  <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle" className="progress-label">
                    <tspan fontSize="24" fontWeight="bold" fill={getScoreColor(evaluationData.overall_score || 0)}>
                      {evaluationData.overall_score?.toFixed(1) || 'N/A'}
                    </tspan>
                    <tspan x="50%" dy="20" fontSize="14" fill="#666">
                      out of 10
                    </tspan>
                  </text>
                </RadialBarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Strengths and Weaknesses */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6" color="success.main">
                  Key Strengths
                </Typography>
              </Box>
              
              {evaluationData.strengths && evaluationData.strengths.length > 0 ? (
                <List dense>
                  {evaluationData.strengths.map((strength, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemIcon>
                        <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText primary={strength} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No specific strengths identified.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingDown sx={{ color: 'error.main', mr: 1 }} />
                <Typography variant="h6" color="error.main">
                  Areas of Concern
                </Typography>
              </Box>
              
              {evaluationData.weaknesses && evaluationData.weaknesses.length > 0 ? (
                <List dense>
                  {evaluationData.weaknesses.map((weakness, index) => (
                    <ListItem key={index} sx={{ pl: 0 }}>
                      <ListItemIcon>
                        <Warning sx={{ color: 'error.main', fontSize: 20 }} />
                      </ListItemIcon>
                      <ListItemText primary={weakness} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No specific weaknesses identified.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Next Steps */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Assignment sx={{ color: 'primary.main', mr: 1 }} />
            <Typography variant="h6" color="primary.main">
              Recommended Next Steps
            </Typography>
          </Box>
          
          {evaluationData.next_steps && evaluationData.next_steps.length > 0 ? (
            <List>
              {evaluationData.next_steps.map((step, index) => (
                <ListItem key={index} sx={{ pl: 0 }}>
                  <ListItemIcon>
                    <Lightbulb sx={{ color: 'primary.main', fontSize: 20 }} />
                  </ListItemIcon>
                  <ListItemText 
                    primary={step}
                    primaryTypographyProps={{ variant: 'body1' }}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No specific next steps provided.
            </Typography>
          )}

          <Divider sx={{ my: 2 }} />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Evaluation completed on {new Date(evaluationData.evaluated_at).toLocaleDateString()}
            </Typography>
            {evaluationData.evaluator_agent_version && (
              <Chip
                label={`Agent v${evaluationData.evaluator_agent_version}`}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default FinalEvaluation;
