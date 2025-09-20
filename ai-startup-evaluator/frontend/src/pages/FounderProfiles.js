import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Avatar,
  Chip,
  Link,
  Alert,
  LinearProgress,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Person,
  LinkedIn,
  Email,
  School,
  Work,
  Star,
  OpenInNew,
} from '@mui/icons-material';
import { apiEndpoints } from '../services/api';

const FounderProfiles = () => {
  const { id } = useParams();

  // Fetch founders data
  const { data: foundersData, isLoading, error } = useQuery(
    ['founders', id],
    () => apiEndpoints.getFounders(id),
    {
      select: (response) => response.data,
      enabled: !!id,
    }
  );

  const getExperienceColor = (years) => {
    if (years >= 10) return 'success';
    if (years >= 5) return 'warning';
    return 'error';
  };

  const getExperienceLabel = (years) => {
    if (years >= 10) return 'Senior';
    if (years >= 5) return 'Experienced';
    if (years >= 2) return 'Mid-level';
    return 'Junior';
  };

  const getRoleIcon = (role) => {
    const roleStr = role?.toLowerCase() || '';
    if (roleStr.includes('ceo') || roleStr.includes('chief executive')) {
      return '👑';
    } else if (roleStr.includes('cto') || roleStr.includes('technical')) {
      return '💻';
    } else if (roleStr.includes('cfo') || roleStr.includes('financial')) {
      return '💰';
    } else if (roleStr.includes('cmo') || roleStr.includes('marketing')) {
      return '📈';
    } else if (roleStr.includes('founder') || roleStr.includes('co-founder')) {
      return '🚀';
    }
    return '👤';
  };

  if (error) {
    return (
      <Alert severity="error">
        Failed to load founder information. Please try again later.
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Loading founder profiles...
        </Typography>
      </Box>
    );
  }

  if (!foundersData || foundersData.length === 0) {
    return (
      <Alert severity="info">
        No founder information available for this startup.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Founding Team ({foundersData.length})
      </Typography>

      <Grid container spacing={3}>
        {foundersData.map((founder, index) => (
          <Grid item xs={12} md={6} key={founder.id || index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                {/* Founder Header */}
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      mr: 2,
                      bgcolor: 'primary.main',
                      fontSize: '2rem',
                    }}
                  >
                    {getRoleIcon(founder.role)}
                  </Avatar>
                  
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h5" gutterBottom>
                      {founder.name || 'Unknown Founder'}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Chip
                        label={founder.role || 'Unknown Role'}
                        color="primary"
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      {founder.years_experience && (
                        <Chip
                          label={`${founder.years_experience}y exp`}
                          color={getExperienceColor(founder.years_experience)}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>

                    {founder.years_experience && (
                      <Typography variant="caption" color="text.secondary">
                        {getExperienceLabel(founder.years_experience)} Level
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Divider sx={{ mb: 2 }} />

                {/* Contact Information */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Contact Information
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {founder.email && (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Email sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                        <Link
                          href={`mailto:${founder.email}`}
                          variant="body2"
                          sx={{ textDecoration: 'none' }}
                        >
                          {founder.email}
                        </Link>
                      </Box>
                    )}
                    
                    {founder.linkedin && (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LinkedIn sx={{ fontSize: 16, mr: 1, color: '#0077b5' }} />
                        <Link
                          href={founder.linkedin}
                          target="_blank"
                          rel="noopener noreferrer"
                          variant="body2"
                          sx={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}
                        >
                          LinkedIn Profile
                          <OpenInNew sx={{ fontSize: 12, ml: 0.5 }} />
                        </Link>
                      </Box>
                    )}
                  </Box>
                </Box>

                {/* Background */}
                {founder.background && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Background
                    </Typography>
                    <Typography variant="body2">
                      {founder.background}
                    </Typography>
                  </Box>
                )}

                {/* Education */}
                {founder.education && (
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <School sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                      <Typography variant="subtitle2" color="text.secondary">
                        Education
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      {founder.education}
                    </Typography>
                  </Box>
                )}

                {/* Previous Experience */}
                {founder.previous_experience && (
                  <Box sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Work sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                      <Typography variant="subtitle2" color="text.secondary">
                        Previous Experience
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      {founder.previous_experience}
                    </Typography>
                  </Box>
                )}

                {/* Experience Summary */}
                <Box sx={{ 
                  mt: 'auto', 
                  pt: 2, 
                  borderTop: '1px solid', 
                  borderColor: 'divider',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Total Experience
                    </Typography>
                    <Typography variant="h6" color="primary">
                      {founder.years_experience ? `${founder.years_experience} years` : 'Not specified'}
                    </Typography>
                  </Box>
                  
                  {founder.years_experience && (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {Array.from({ length: 5 }, (_, i) => (
                        <Star
                          key={i}
                          sx={{
                            fontSize: 16,
                            color: i < Math.min(founder.years_experience / 2, 5) ? 'warning.main' : 'action.disabled'
                          }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Team Summary */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Team Analysis Summary
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {foundersData.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Founders
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="secondary">
                  {foundersData.reduce((sum, founder) => sum + (founder.years_experience || 0), 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Years Experience
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {Math.round(foundersData.reduce((sum, founder) => sum + (founder.years_experience || 0), 0) / foundersData.length) || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average Experience
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {foundersData.filter(f => f.linkedin).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  LinkedIn Profiles
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Team Strengths */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Team Strengths
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {foundersData.some(f => f.years_experience >= 10) && (
                <Chip label="Senior Leadership" color="success" size="small" />
              )}
              {foundersData.some(f => f.role?.toLowerCase().includes('technical')) && (
                <Chip label="Technical Expertise" color="info" size="small" />
              )}
              {foundersData.some(f => f.role?.toLowerCase().includes('business')) && (
                <Chip label="Business Experience" color="primary" size="small" />
              )}
              {foundersData.filter(f => f.linkedin).length === foundersData.length && (
                <Chip label="Strong Online Presence" color="secondary" size="small" />
              )}
              {foundersData.length >= 2 && (
                <Chip label="Diverse Founding Team" color="warning" size="small" />
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default FounderProfiles;
