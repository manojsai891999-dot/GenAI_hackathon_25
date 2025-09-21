import React from 'react';
import { useOutletContext } from 'react-router-dom';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  Business,
  LocationOn,
  CalendarToday,
  People,
  TrendingUp,
  AttachMoney,
  Timeline,
  Speed,
} from '@mui/icons-material';
import { format } from 'date-fns';

const StartupOverview = () => {
  const { startupData } = useOutletContext();

  const InfoCard = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {React.cloneElement(icon, { sx: { color: `${color}.main`, mr: 1 } })}
          <Typography variant="h6" color={`${color}.main`}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" fontWeight="bold">
          {value || 'N/A'}
        </Typography>
      </CardContent>
    </Card>
  );

  const MetricCard = ({ title, value, subtitle, progress, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h5" fontWeight="bold" color={`${color}.main`} gutterBottom>
          {value || 'N/A'}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
        {progress !== undefined && (
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ mt: 1, height: 6, borderRadius: 3 }}
            color={color}
          />
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Company Information */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Company Overview
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Sector"
            value={startupData?.sector}
            icon={<Business />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Stage"
            value={startupData?.stage}
            icon={<Timeline />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Location"
            value={startupData?.location}
            icon={<LocationOn />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Founded"
            value={startupData?.founded_year}
            icon={<CalendarToday />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Financial Metrics */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Financial Metrics
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Annual Revenue"
            value={startupData?.formattedRevenue}
            subtitle={startupData?.revenue ? `$${startupData.revenue.toLocaleString()}` : null}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Annual Recurring Revenue"
            value={startupData?.arr ? `$${(startupData.arr / 1000000).toFixed(1)}M` : 'N/A'}
            subtitle={startupData?.arr ? `$${startupData.arr.toLocaleString()}` : null}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Total Funding Raised"
            value={startupData?.formattedFunding}
            subtitle={startupData?.funding_raised ? `$${startupData.funding_raised.toLocaleString()}` : null}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Valuation"
            value={startupData?.formattedValuation}
            subtitle={startupData?.valuation ? `$${startupData.valuation.toLocaleString()}` : null}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Monthly Burn Rate"
            value={startupData?.burn_rate ? `$${(startupData.burn_rate / 1000).toFixed(0)}K` : 'N/A'}
            subtitle={startupData?.burn_rate ? `$${startupData.burn_rate.toLocaleString()}/month` : null}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Runway"
            value={startupData?.runway_months ? `${startupData.runway_months} months` : 'N/A'}
            subtitle={startupData?.runway_months && startupData.runway_months < 12 ? 'Consider fundraising' : null}
            progress={startupData?.runway_months ? Math.min((startupData.runway_months / 24) * 100, 100) : 0}
            color={startupData?.runway_months < 6 ? 'error' : startupData?.runway_months < 12 ? 'warning' : 'success'}
          />
        </Grid>
      </Grid>

      {/* Unit Economics */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Unit Economics & Growth
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Customer Acquisition Cost"
            value={startupData?.formattedCAC}
            subtitle="CAC"
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Lifetime Value"
            value={startupData?.formattedLTV}
            subtitle="LTV"
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="LTV/CAC Ratio"
            value={startupData?.ltvCacRatio ? `${startupData.ltvCacRatio}:1` : 'N/A'}
            subtitle={startupData?.ltvCacRatio >= 3 ? 'Healthy ratio' : 'Needs improvement'}
            color={startupData?.ltvCacRatio >= 3 ? 'success' : 'warning'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Team Size"
            value={startupData?.team_size}
            subtitle="employees"
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={6}>
          <MetricCard
            title="Monthly Growth Rate"
            value={startupData?.formattedGrowthRate}
            subtitle={startupData?.growth_rate > 0.1 ? 'Strong growth' : startupData?.growth_rate > 0.05 ? 'Moderate growth' : 'Slow growth'}
            progress={startupData?.growth_rate ? Math.min(startupData.growth_rate * 500, 100) : 0}
            color={startupData?.growth_rate > 0.1 ? 'success' : startupData?.growth_rate > 0.05 ? 'warning' : 'error'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={6}>
          <MetricCard
            title="Monthly Churn Rate"
            value={startupData?.formattedChurnRate}
            subtitle={startupData?.churn_rate < 0.05 ? 'Excellent retention' : startupData?.churn_rate < 0.1 ? 'Good retention' : 'High churn'}
            progress={startupData?.churn_rate ? 100 - (startupData.churn_rate * 1000) : 0}
            color={startupData?.churn_rate < 0.05 ? 'success' : startupData?.churn_rate < 0.1 ? 'warning' : 'error'}
          />
        </Grid>
      </Grid>

      {/* Company Details */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Company Details
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Description
                </Typography>
                <Typography variant="body1">
                  {startupData?.description || 'No description available'}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Website
                </Typography>
                {startupData?.website ? (
                  <Typography
                    variant="body1"
                    component="a"
                    href={startupData.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    sx={{ color: 'primary.main', textDecoration: 'none' }}
                  >
                    {startupData.website}
                  </Typography>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    Not provided
                  </Typography>
                )}
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Last Updated
                </Typography>
                <Typography variant="body1">
                  {startupData?.updated_at 
                    ? format(new Date(startupData.updated_at), 'PPP')
                    : format(new Date(startupData?.created_at || Date.now()), 'PPP')
                  }
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Analysis Status
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    label="Data Extracted"
                    color="success"
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label="Benchmarks Available"
                    color="info"
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    label="Risk Analysis Complete"
                    color="warning"
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default StartupOverview;
