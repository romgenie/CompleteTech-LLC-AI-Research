import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Avatar,
  Icon
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ExploreIcon from '@mui/icons-material/Explore';
import ScheduleIcon from '@mui/icons-material/Schedule';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import AssignmentIcon from '@mui/icons-material/Assignment';
import { ResearchInsight, Tag } from '../types/research';

interface ResearchInsightCardProps {
  insight: ResearchInsight;
}

/**
 * Card component for displaying a research insight or suggestion
 */
const ResearchInsightCard: React.FC<ResearchInsightCardProps> = ({
  insight
}) => {
  const { type, title, description, importance, iconType, relatedTags } = insight;

  // Get icon based on insight type
  const getIconComponent = () => {
    switch (iconType) {
      case 'trending_up':
        return <TrendingUpIcon />;
      case 'explore':
        return <ExploreIcon />;
      case 'schedule':
        return <ScheduleIcon />;
      case 'lightbulb':
        return <LightbulbIcon />;
      case 'analytics':
        return <EqualizerIcon />;
      case 'assignment':
        return <AssignmentIcon />;
      default:
        // Default icons based on type
        switch (type) {
          case 'trend':
            return <TrendingUpIcon />;
          case 'gap':
            return <ExploreIcon />;
          case 'pattern':
            return <EqualizerIcon />;
          case 'suggestion':
            return <LightbulbIcon />;
          default:
            return <LightbulbIcon />;
        }
    }
  };

  // Get color based on importance
  const getImportanceColor = () => {
    switch (importance) {
      case 'high':
        return '#F44336'; // red
      case 'medium':
        return '#2196F3'; // blue
      case 'low':
        return '#4CAF50'; // green
      default:
        return '#9E9E9E'; // gray
    }
  };

  // Get background color based on insight type
  const getBackgroundColor = () => {
    switch (type) {
      case 'trend':
        return 'rgba(33, 150, 243, 0.08)'; // blue bg
      case 'gap':
        return 'rgba(156, 39, 176, 0.08)'; // purple bg
      case 'pattern':
        return 'rgba(76, 175, 80, 0.08)'; // green bg
      case 'suggestion':
        return 'rgba(255, 152, 0, 0.08)'; // orange bg
      default:
        return 'rgba(158, 158, 158, 0.08)'; // gray bg
    }
  };

  return (
    <Card 
      variant="outlined" 
      sx={{ 
        backgroundColor: getBackgroundColor(),
        borderLeft: `5px solid ${getImportanceColor()}`,
        height: '100%',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" mb={2}>
          <Avatar
            sx={{ 
              bgcolor: getImportanceColor(),
              mr: 2,
              width: 40,
              height: 40
            }}
          >
            {getIconComponent()}
          </Avatar>
          <Box>
            <Typography variant="subtitle1" component="div" gutterBottom>
              {title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          </Box>
        </Box>
        
        {relatedTags && relatedTags.length > 0 && (
          <Box mt={2}>
            {relatedTags.map((tag: Tag) => (
              <Chip 
                key={tag.id}
                label={tag.name}
                size="small"
                sx={{ 
                  mr: 0.5, 
                  mb: 0.5,
                  backgroundColor: tag.color,
                  color: tag.color && isColorDark(tag.color) ? 'white' : 'inherit'
                }}
              />
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

// Utility function to determine if a color is dark
function isColorDark(hexColor: string): boolean {
  // Remove the hash if it exists
  hexColor = hexColor.replace('#', '');
  
  // Parse the hex color
  const r = parseInt(hexColor.substr(0, 2), 16);
  const g = parseInt(hexColor.substr(2, 2), 16);
  const b = parseInt(hexColor.substr(4, 2), 16);
  
  // Calculate perceived brightness (YIQ formula)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  
  // Return true if the color is dark
  return yiq < 128;
}

export default ResearchInsightCard;