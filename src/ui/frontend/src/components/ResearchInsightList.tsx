import React from 'react';
import {
  Box,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Paper,
  Divider
} from '@mui/material';
import InsightsIcon from '@mui/icons-material/Insights';
import { ResearchInsight } from '../types/research';
import ResearchInsightCard from './ResearchInsightCard';

interface ResearchInsightListProps {
  insights: ResearchInsight[];
  loading?: boolean;
  error?: Error | null;
}

/**
 * Component for displaying a list of research insights
 */
const ResearchInsightList: React.FC<ResearchInsightListProps> = ({
  insights,
  loading = false,
  error = null
}) => {
  // If loading, show spinner
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  // If error, show error message
  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load insights: {error.message}
      </Alert>
    );
  }

  // If no insights, show message
  if (insights.length === 0) {
    return (
      <Paper variant="outlined" sx={{ p: 3, my: 2 }}>
        <Typography variant="body1" color="text.secondary" align="center">
          Not enough research data to generate insights yet.
        </Typography>
      </Paper>
    );
  }

  // Group insights by importance
  const highImportance = insights.filter(i => i.importance === 'high');
  const mediumImportance = insights.filter(i => i.importance === 'medium');
  const lowImportance = insights.filter(i => i.importance === 'low');

  return (
    <Box>
      <Box mb={2} display="flex" alignItems="center">
        <InsightsIcon color="primary" sx={{ mr: 1 }} />
        <Typography variant="h6">
          Research Insights
        </Typography>
      </Box>
      
      {highImportance.length > 0 && (
        <Box mb={4}>
          <Typography variant="subtitle2" color="error" gutterBottom>
            Key Insights
          </Typography>
          <Grid container spacing={2}>
            {highImportance.map(insight => (
              <Grid item xs={12} md={6} key={insight.id}>
                <ResearchInsightCard insight={insight} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {mediumImportance.length > 0 && (
        <Box mb={4}>
          {highImportance.length > 0 && <Divider sx={{ mb: 2 }} />}
          <Typography variant="subtitle2" color="primary" gutterBottom>
            Helpful Patterns
          </Typography>
          <Grid container spacing={2}>
            {mediumImportance.map(insight => (
              <Grid item xs={12} md={6} key={insight.id}>
                <ResearchInsightCard insight={insight} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {lowImportance.length > 0 && (
        <Box>
          {(highImportance.length > 0 || mediumImportance.length > 0) && 
            <Divider sx={{ mb: 2 }} />
          }
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Other Observations
          </Typography>
          <Grid container spacing={2}>
            {lowImportance.map(insight => (
              <Grid item xs={12} md={6} key={insight.id}>
                <ResearchInsightCard insight={insight} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default ResearchInsightList;