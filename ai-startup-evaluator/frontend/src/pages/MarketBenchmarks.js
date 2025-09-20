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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/icons-material';
import { apiEndpoints } from '../services/api';

const MarketBenchmarks = () => {
  const { id } = useParams();

  const { data: benchmarksData, isLoading, error } = useQuery(
    ['benchmarks', id],
    () => apiEndpoints.getBenchmarks(id),
    {
      select: (response) => response.data,
      enabled: !!id,
    }
  );

  const getComparisonIcon = (result) => {
    switch (result) {
      case 'above':
        return <TrendingUp sx={{ color: 'success.main' }} />;
      case 'below':
        return <TrendingDown sx={{ color: 'error.main' }} />;
      default:
        return <TrendingFlat sx={{ color: 'warning.main' }} />;
    }
  };

  const getComparisonColor = (result) => {
    switch (result) {
      case 'above':
        return 'success';
      case 'below':
        return 'error';
      default:
        return 'warning';
    }
  };

  if (error) {
    return (
      <Alert severity="error">
        Failed to load benchmark data. Please try again later.
      </Alert>
    );
  }

  if (isLoading) {
    return (
      <Box>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Loading market benchmarks...
        </Typography>
      </Box>
    );
  }

  if (!benchmarksData || benchmarksData.length === 0) {
    return (
      <Alert severity="info">
        No benchmark data available for this startup.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Market Benchmarks & Comparisons
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {benchmarksData.slice(0, 4).map((benchmark, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                  {getComparisonIcon(benchmark.comparison_result)}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {benchmark.metric_name?.replace('_', ' ').toUpperCase()}
                  </Typography>
                </Box>
                
                <Typography variant="h4" color="primary" gutterBottom>
                  {benchmark.startup_value?.toFixed(1) || 'N/A'}
                </Typography>
                
                <Chip
                  label={benchmark.comparison_result?.replace('_', ' ') || 'Unknown'}
                  color={getComparisonColor(benchmark.comparison_result)}
                  size="small"
                />
                
                {benchmark.percentile_rank && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {benchmark.percentile_rank.toFixed(0)}th percentile
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detailed Benchmark Comparison
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell align="right">Startup Value</TableCell>
                  <TableCell align="right">Industry Median</TableCell>
                  <TableCell align="right">25th Percentile</TableCell>
                  <TableCell align="right">75th Percentile</TableCell>
                  <TableCell align="center">Comparison</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {benchmarksData.map((benchmark, index) => (
                  <TableRow key={index}>
                    <TableCell component="th" scope="row">
                      {benchmark.metric_name?.replace('_', ' ').toUpperCase()}
                    </TableCell>
                    <TableCell align="right">
                      <Typography fontWeight="bold">
                        {benchmark.startup_value?.toFixed(2) || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {benchmark.benchmark_median?.toFixed(2) || 'N/A'}
                    </TableCell>
                    <TableCell align="right">
                      {benchmark.benchmark_p25?.toFixed(2) || 'N/A'}
                    </TableCell>
                    <TableCell align="right">
                      {benchmark.benchmark_p75?.toFixed(2) || 'N/A'}
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {getComparisonIcon(benchmark.comparison_result)}
                        <Chip
                          label={benchmark.comparison_result?.replace('_', ' ') || 'Unknown'}
                          color={getComparisonColor(benchmark.comparison_result)}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MarketBenchmarks;
