import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Collapse,
  IconButton,
  Divider,
  CircularProgress,
  Alert,
  Fade,
  Paper
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { ResearchRecommendationGroup } from '../types/research';
import ResearchRecommendationCard from './ResearchRecommendationCard';

interface ResearchRecommendationListProps {
  recommendationGroups: ResearchRecommendationGroup[];
  onUseRecommendation: (query: string) => void;
  onSaveRecommendation?: (id: string) => void;
  savedRecommendations?: string[];
  loading?: boolean;
  error?: Error | null;
}

/**
 * Component for displaying groups of research recommendations
 */
const ResearchRecommendationList: React.FC<ResearchRecommendationListProps> = ({
  recommendationGroups,
  onUseRecommendation,
  onSaveRecommendation,
  savedRecommendations = [],
  loading = false,
  error = null
}) => {
  // Track which groups are expanded (default all expanded)
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(
    recommendationGroups.reduce((acc, group) => {
      acc[group.id] = true;
      return acc;
    }, {} as Record<string, boolean>)
  );

  // Toggle group expansion
  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  };

  // If loading, show spinner
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={6}>
        <CircularProgress />
      </Box>
    );
  }

  // If error, show error message
  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load recommendations: {error.message}
      </Alert>
    );
  }

  // If no recommendations, show message
  if (recommendationGroups.length === 0) {
    return (
      <Paper elevation={0} variant="outlined" sx={{ p: 3, my: 2 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <InfoOutlinedIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6">No Recommendations Yet</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          As you save more research queries and add tags, we'll generate personalized recommendations to help you explore new research areas.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {recommendationGroups.map(group => (
        <Fade key={group.id} in={true} timeout={500}>
          <Box mb={4}>
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center"
              onClick={() => toggleGroup(group.id)}
              sx={{ cursor: 'pointer' }}
            >
              <Box>
                <Typography variant="h6" component="h3">
                  {group.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {group.description}
                </Typography>
              </Box>
              <IconButton size="small">
                {expandedGroups[group.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Collapse in={expandedGroups[group.id]} timeout="auto" unmountOnExit>
              <Grid container spacing={3}>
                {group.recommendations.map(recommendation => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={recommendation.id}>
                    <ResearchRecommendationCard
                      recommendation={recommendation}
                      onUseRecommendation={onUseRecommendation}
                      onSaveRecommendation={onSaveRecommendation}
                      isSaved={savedRecommendations.includes(recommendation.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Collapse>
          </Box>
        </Fade>
      ))}
    </Box>
  );
};

export default ResearchRecommendationList;