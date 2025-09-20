import React from 'react';
import { useParams, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  Alert,
  LinearProgress,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Business,
  People,
  TrendingUp,
  Warning,
  Mic,
  Description,
  Assessment,
  Home,
} from '@mui/icons-material';
import { apiEndpoints, apiHelpers } from '../services/api';

const StartupDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  // Fetch complete startup data
  const { data: startupData, isLoading, error } = useQuery(
    ['startup', id],
    () => apiEndpoints.getStartupComplete(id),
    {
      select: (response) => apiHelpers.formatStartupData(response.data),
      enabled: !!id,
    }
  );

  const tabs = [
    { label: 'Overview', path: '', icon: <Business /> },
    { label: 'Founders', path: 'founders', icon: <People /> },
    { label: 'Benchmarks', path: 'benchmarks', icon: <TrendingUp /> },
    { label: 'Risks', path: 'risks', icon: <Warning /> },
    { label: 'Interview', path: 'interview', icon: <Mic /> },
    { label: 'Memo', path: 'memo', icon: <Description /> },
    { label: 'Evaluation', path: 'evaluation', icon: <Assessment /> },
  ];

  const getCurrentTabIndex = () => {
    const currentPath = location.pathname.split('/').pop();
    const tabIndex = tabs.findIndex(tab => tab.path === currentPath);
    return tabIndex >= 0 ? tabIndex : 0;
  };

  const handleTabChange = (event, newValue) => {
    const selectedTab = tabs[newValue];
    const newPath = selectedTab.path 
      ? `/startup/${id}/${selectedTab.path}`
      : `/startup/${id}`;
    navigate(newPath);
  };

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to load startup data. Please try again later.
        </Alert>
      </Container>
    );
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
            Loading startup data...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          color="inherit"
          href="/"
          onClick={(e) => {
            e.preventDefault();
            navigate('/');
          }}
          sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
        >
          <Home sx={{ mr: 0.5, fontSize: 20 }} />
          Dashboard
        </Link>
        <Typography color="text.primary">
          {startupData?.name || 'Startup Details'}
        </Typography>
      </Breadcrumbs>

      {/* Startup Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {startupData?.name || 'Unknown Startup'}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                {startupData?.description || 'No description available'}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <Chip
                  label={startupData?.sector || 'Unknown Sector'}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={startupData?.stage || 'Unknown Stage'}
                  color="secondary"
                  variant="outlined"
                />
                {startupData?.location && (
                  <Chip
                    label={startupData.location}
                    variant="outlined"
                  />
                )}
              </Box>
            </Box>

            {/* Quick Stats */}
            <Box sx={{ display: 'flex', gap: 3, textAlign: 'right' }}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Revenue
                </Typography>
                <Typography variant="h6" color="primary">
                  {startupData?.formattedRevenue || 'N/A'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Funding
                </Typography>
                <Typography variant="h6" color="secondary">
                  {startupData?.formattedFunding || 'N/A'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Team Size
                </Typography>
                <Typography variant="h6">
                  {startupData?.team_size || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Box>

          {/* Key Metrics Row */}
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
            gap: 2, 
            mt: 3,
            pt: 2,
            borderTop: '1px solid',
            borderColor: 'divider'
          }}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Growth Rate
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {startupData?.formattedGrowthRate || 'N/A'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Churn Rate
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {startupData?.formattedChurnRate || 'N/A'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                CAC
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {startupData?.formattedCAC || 'N/A'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                LTV
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {startupData?.formattedLTV || 'N/A'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                LTV/CAC Ratio
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {startupData?.ltvCacRatio || 'N/A'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Runway
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {startupData?.runway_months ? `${startupData.runway_months}mo` : 'N/A'}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Navigation Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={getCurrentTabIndex()}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={tab.path}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
              sx={{ minHeight: 64 }}
            />
          ))}
        </Tabs>
      </Card>

      {/* Tab Content */}
      <Outlet context={{ startupData }} />
    </Container>
  );
};

export default StartupDetail;
