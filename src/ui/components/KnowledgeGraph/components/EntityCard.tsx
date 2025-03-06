/**
 * Knowledge Graph entity card component (stub implementation)
 */
import React from 'react';
import { Box, Card, CardContent, Typography, Chip, CardActions, Button } from '@mui/material';
import { Entity } from '../types/knowledgeGraph.types';
import { getEntityColor } from '../utils/knowledgeGraphUtils';

interface EntityCardProps {
  item: Entity;
  onSelect?: (item: Entity) => void;
  onDelete?: (id: string) => void;
  readOnly?: boolean;
}

export const EntityCard: React.FC<EntityCardProps> = ({
  item,
  onSelect,
  onDelete,
  readOnly = false
}) => {
  return (
    <Card variant="outlined" sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      '&:hover': {
        boxShadow: 2
      }
    }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="subtitle1" component="h3" noWrap>
            {item.name}
          </Typography>
          <Chip 
            label={item.type} 
            size="small"
            sx={{ 
              backgroundColor: getEntityColor(item.type),
              color: 'white',
              fontSize: '0.7rem'
            }}
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {item.description || 'No description'}
        </Typography>
        
        {item.confidence !== undefined && (
          <Box sx={{ mt: 'auto' }}>
            <Chip 
              label={`Confidence: ${Math.round(item.confidence * 100)}%`} 
              size="small"
              color={item.confidence > 0.8 ? 'success' : item.confidence > 0.5 ? 'warning' : 'error'}
            />
          </Box>
        )}
      </CardContent>
      
      <CardActions>
        <Button size="small" onClick={() => onSelect && onSelect(item)}>
          View
        </Button>
        {!readOnly && onDelete && (
          <Button size="small" color="error" onClick={() => onDelete(item.id)}>
            Delete
          </Button>
        )}
      </CardActions>
    </Card>
  );
};