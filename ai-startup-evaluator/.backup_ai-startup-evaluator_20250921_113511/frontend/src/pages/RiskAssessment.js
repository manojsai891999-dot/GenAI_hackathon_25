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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Warning,
  Error,
  CheckCircle,
  ExpandMore,
  Business,
  People,
  TrendingUp,
  Build,
  Gavel,
} from '@mui/icons-material';
import { apiEndpoints, apiHelpers } from '../services/api';

const RiskAssessment = () => {
  const { id } = useParams();

  const { data: risksData, isLoading, error } = useQuery(
    ['risks', id],
    () => apiEndpoints.getRisks(id),
    {
      select: (response) => response.data,
      enabled: !!id,
    }
  );

  const getCategoryIcon = (category) => {
    switch (category?.toLowerCase()) {
      case 'financial':
        return <TrendingUp />;
      case 'team':
        return <People />;
      case 'market':
        return <Business />;
      case 'product':
        return <Build />;
      case 'regulatory':
        return <Gavel />;
      default:
        return <Warning />;
    }
  };

  const getSeverityConfig = (severity) => {
    return apiHelpers.formatRiskSeverity(severity);
  };

  if (error) {
    return (
      <Alert severity="error">
        Failed to load risk assessment data. Please try again later.
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Loading risk assessment...
        </Typography>
      </Box>
    );
  }

  if (!risksData || risksData.length === 0) {
    return (
      <Alert severity="success" icon={<CheckCircle />}>
        No significant risks identified for this startup.
      </Alert>
    );
  }

  // Group risks by category
  const risksByCategory = risksData.reduce((acc, risk) => {
    const category = risk.category || 'other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(risk);
    return acc;
  }, {});

  // Count risks by severity
  const riskCounts = risksData.reduce((acc, risk) => {
    const severity = risk.severity || 'unknown';
    acc[severity] = (acc[severity] || 0) + 1;
    return acc;
  }, {});

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Risk Assessment Overview
      </Typography>

      {/* Risk Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Error sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
              <Typography variant="h4" color="error.main">
                {riskCounts.red || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                High Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Warning sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" color="warning.main">
                {riskCounts.yellow || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Medium Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
              <Typography variant="h4" color="success.main">
                {riskCounts.green || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Low Risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Warning sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="h4" color="primary.main">
                {risksData.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Risks
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Risks by Category */}
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Risk Categories
      </Typography>

      {Object.entries(risksByCategory).map(([category, risks]) => (
        <Accordion key={category} sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
              {getCategoryIcon(category)}
              <Typography variant="h6" sx={{ ml: 1, flexGrow: 1 }}>
                {category.charAt(0).toUpperCase() + category.slice(1)} Risks
              </Typography>
              <Chip
                label={`${risks.length} risk${risks.length !== 1 ? 's' : ''}`}
                size="small"
                color="primary"
                sx={{ mr: 2 }}
              />
            </Box>
          </AccordionSummary>
          
          <AccordionDetails>
            <List>
              {risks.map((risk, index) => {
                const severityConfig = getSeverityConfig(risk.severity);
                
                return (
                  <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                      <ListItemIcon sx={{ minWidth: 'auto', mr: 1 }}>
                        <Typography sx={{ fontSize: 20 }}>
                          {severityConfig.icon}
                        </Typography>
                      </ListItemIcon>
                      
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {risk.risk_type?.replace('_', ' ').toUpperCase()}
                            </Typography>
                            <Chip
                              label={severityConfig.label}
                              size="small"
                              sx={{ 
                                backgroundColor: severityConfig.color,
                                color: 'white',
                                fontWeight: 'bold'
                              }}
                            />
                          </Box>
                        }
                        secondary={risk.description}
                      />
                    </Box>
                    
                    {/* Risk Scores */}
                    <Box sx={{ display: 'flex', gap: 2, mb: 1, ml: 4 }}>
                      {risk.impact_score && (
                        <Typography variant="caption" color="text.secondary">
                          Impact: {risk.impact_score}/10
                        </Typography>
                      )}
                      {risk.likelihood_score && (
                        <Typography variant="caption" color="text.secondary">
                          Likelihood: {risk.likelihood_score}/10
                        </Typography>
                      )}
                    </Box>
                    
                    {/* Mitigation Suggestions */}
                    {risk.mitigation_suggestions && (
                      <Box sx={{ ml: 4, p: 2, bgcolor: 'background.default', borderRadius: 1, width: '100%' }}>
                        <Typography variant="caption" color="text.secondary" fontWeight="bold">
                          Mitigation Strategy:
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 0.5 }}>
                          {risk.mitigation_suggestions}
                        </Typography>
                      </Box>
                    )}
                  </ListItem>
                );
              })}
            </List>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

export default RiskAssessment;
