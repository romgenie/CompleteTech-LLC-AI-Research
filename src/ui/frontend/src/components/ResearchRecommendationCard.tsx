import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Button,
  Tooltip,
  IconButton
} from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { ResearchRecommendation, Tag } from '../types/research';

interface ResearchRecommendationCardProps {
  recommendation: ResearchRecommendation;
  onUseRecommendation: (query: string) => void;
  onSaveRecommendation?: (id: string) => void;
  isSaved?: boolean;
}

/**
 * Card component for displaying a single research recommendation
 */
const ResearchRecommendationCard: React.FC<ResearchRecommendationCardProps> = ({
  recommendation,
  onUseRecommendation,
  onSaveRecommendation,
  isSaved = false
}) => {
  const { id, title, description, confidence, basedOn, tags, suggestedQueryText } = recommendation;

  // Calculate confidence percentage and color
  const confidencePercent = Math.round(confidence * 100);
  const confidenceColor = 
    confidencePercent >= 85 ? 'success.main' : 
    confidencePercent >= 70 ? 'primary.main' : 
    'warning.main';

  // Generate tooltip explanation
  const getSourceExplanation = () => {
    const sources = basedOn.map(source => {
      switch (source.type) {
        case 'tag':
          return `Your interest in "${source.tagName}"`;
        case 'query':
          return `Your previous query: "${source.queryText}"`;
        case 'history':
          return source.patternDescription;
        default:
          return "Unknown source";
      }
    });

    return (
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          This recommendation is based on:
        </Typography>
        <ul style={{ margin: 0, paddingLeft: '1rem' }}>
          {sources.map((source, idx) => (
            <li key={idx}>
              <Typography variant="body2">{source}</Typography>
            </li>
          ))}
        </ul>
      </Box>
    );
  };

  return (
    <Card 
      variant="outlined" 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 2
        }
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Tooltip title={isSaved ? "Saved" : "Save for later"}>
            <IconButton 
              size="small"
              onClick={() => onSaveRecommendation?.(id)}
              color={isSaved ? "primary" : "default"}
            >
              {isSaved ? <BookmarkIcon /> : <BookmarkBorderIcon />}
            </IconButton>
          </Tooltip>
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          {description}
        </Typography>
        
        {tags && tags.length > 0 && (
          <Box mt={2} mb={1}>
            {tags.map((tag: Tag) => (
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
        
        <Box mt={2} display="flex" alignItems="center">
          <Box flexGrow={1} mr={1}>
            <LinearProgress 
              variant="determinate" 
              value={confidencePercent} 
              sx={{ 
                height: 8, 
                borderRadius: 1,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: confidenceColor
                }
              }} 
            />
          </Box>
          <Box display="flex" alignItems="center">
            <Typography 
              variant="body2" 
              color={confidenceColor}
              sx={{ fontWeight: 'bold', mr: 0.5 }}
            >
              {confidencePercent}%
            </Typography>
            <Tooltip 
              title={getSourceExplanation()} 
              placement="top"
              arrow
            >
              <IconButton size="small">
                <HelpOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </CardContent>
      
      <CardActions>
        <Button 
          fullWidth
          variant="contained"
          size="small"
          onClick={() => onUseRecommendation(suggestedQueryText || title)}
          endIcon={<ArrowForwardIcon />}
        >
          Explore this Topic
        </Button>
      </CardActions>
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

export default ResearchRecommendationCard;