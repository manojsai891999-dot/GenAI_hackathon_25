import React from 'react';
import { useQuery } from 'react-query';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  Business,
  Assessment,
  Upload,
  Visibility,
  Edit,
  Delete,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { apiEndpoints, apiHelpers } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();

  // Fetch statistics
  const { data: statsData, isLoading: statsLoading, error: statsError } = useQuery(
    'stats',
    () => apiEndpoints.getStats(),
    {
      select: (response) => response.data.data,
    }
  );

  // Fetch startups list
  const { data: startupsData, isLoading: startupsLoading, error: startupsError } = useQuery(
    'startups',
    () => apiEndpoints.listStartups({ limit: 10 }),
    {
      select: (response) => response.data.map(apiHelpers.formatStartupData),
    }
  );

  const handleViewStartup = (startupId) => {
    navigate(`/startup/${startupId}`);
  };

  const handleUploadNew = () => {
    navigate('/upload');
  };

  // Prepare chart data
  const recommendationData = statsData ? [
    { name: 'Recommend', value: statsData.recommendations.pass, color: '#4caf50' },
    { name: 'Conditional', value: statsData.recommendations.maybe, color: '#ff9800' },
    { name: 'Reject', value: statsData.recommendations.reject, color: '#f44336' },
  ] : [];

  const sectorData = statsData ? Object.entries(statsData.by_sector).map(([sector, count]) => ({
    sector,
    count,
  })) : [];

  if (statsError || startupsError) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to load dashboard data. Please try again later.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Investment Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          AI-powered startup evaluation and analysis platform
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Business sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="h6">Total Startups</Typography>
              </Box>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <Typography variant="h3" color="primary">
                  {statsData?.total_startups || 0}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assessment sx={{ color: 'secondary.main', mr: 1 }} />
                <Typography variant="h6">Evaluations</Typography>
              </Box>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <Typography variant="h3" color="secondary">
                  {statsData?.total_evaluations || 0}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="h6">Recommended</Typography>
              </Box>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <Typography variant="h3" color="success.main">
                  {statsData?.recommendations.pass || 0}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, justifyContent: 'space-between' }}>
                <Typography variant="h6">Quick Actions</Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<Upload />}
                onClick={handleUploadNew}
                fullWidth
                sx={{ mt: 1 }}
              >
                Upload Pitch Deck
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Investment Recommendations
              </Typography>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={recommendationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {recommendationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Startups by Sector
              </Typography>
              {statsLoading ? (
                <LinearProgress />
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={sectorData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="sector" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="count" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Startups */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Recent Startups</Typography>
            <Button
              variant="outlined"
              onClick={() => navigate('/startups')}
              size="small"
            >
              View All
            </Button>
          </Box>

          {startupsLoading ? (
            <LinearProgress />
          ) : startupsData && startupsData.length > 0 ? (
            <Grid container spacing={2}>
              {startupsData.map((startup) => (
                <Grid item xs={12} key={startup.id}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Typography variant="h6" sx={{ mr: 2 }}>
                            {startup.name}
                          </Typography>
                          <Chip
                            label={startup.sector}
                            size="small"
                            color="primary"
                            variant="outlined"
                            sx={{ mr: 1 }}
                          />
                          <Chip
                            label={startup.stage}
                            size="small"
                            color="secondary"
                            variant="outlined"
                          />
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {startup.description || 'No description available'}
                        </Typography>

                        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Revenue
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {startup.formattedRevenue}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Funding
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {startup.formattedFunding}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Team Size
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {startup.team_size || 'N/A'}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Location
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {startup.location || 'N/A'}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>

                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => handleViewStartup(startup.id)}
                            color="primary"
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/startup/${startup.id}/edit`)}
                            color="default"
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                No startups evaluated yet
              </Typography>
              <Button
                variant="contained"
                startIcon={<Upload />}
                onClick={handleUploadNew}
                sx={{ mt: 2 }}
              >
                Upload Your First Pitch Deck
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default Dashboard;
