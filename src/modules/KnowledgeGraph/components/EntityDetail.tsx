/**
 * Knowledge Graph entity detail component (stub implementation)
 */
import React from 'react';
import { 
  Box, 
  Typography, 
  Chip, 
  Divider, 
  Button, 
  Paper, 
  Grid,
  List,
  ListItem,
  ListItemText,
  IconButton,
  CircularProgress,
  Alert
} from '@mui/material';
import { ArrowBack, Edit, Delete } from '@mui/icons-material';
import { Entity } from '../types/knowledgeGraph.types';
import { getEntityColor, formatEntity } from '../utils/knowledgeGraphUtils';

interface EntityDetailProps {
  entity: Entity | null;
  loading: boolean;
  error: Error | null;
  onEdit?: (entity: Entity) => void;
  onDelete?: (id: string) => void;
  readOnly?: boolean;
  onBack?: () => void;
}

export const EntityDetail: React.FC<EntityDetailProps> = ({
  entity,
  loading,
  error,
  onEdit,
  onDelete,
  readOnly = false,
  onBack
}) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Alert severity="error">{error.message}</Alert>
      </Box>
    );
  }

  if (!entity) {
    return (
      <Box p={2}>
        <Alert severity="info">No entity selected.</Alert>
        {onBack && (
          <Button 
            startIcon={<ArrowBack />} 
            onClick={onBack} 
            sx={{ mt: 2 }}
          >
            Back to List
          </Button>
        )}
      </Box>
    );
  }

  return (
    <Box p={2}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        {onBack && (
          <IconButton onClick={onBack} sx={{ mr: 1 }}>
            <ArrowBack />
          </IconButton>
        )}
        <Typography variant="h5" component="h2">
          {entity.name}
        </Typography>
        <Chip 
          label={entity.type} 
          size="small"
          sx={{ 
            ml: 1,
            backgroundColor: getEntityColor(entity.type),
            color: 'white',
          }}
        />
        {entity.confidence !== undefined && (
          <Chip 
            label={`${Math.round(entity.confidence * 100)}%`} 
            size="small"
            color={entity.confidence > 0.8 ? 'success' : entity.confidence > 0.5 ? 'warning' : 'error'}
            sx={{ ml: 1 }}
          />
        )}
      </Box>
      
      {entity.description && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body1">{entity.description}</Typography>
        </Box>
      )}
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="h6">Properties</Typography>
      <Paper variant="outlined" sx={{ mt: 1, mb: 3 }}>
        <List dense>
          {Object.entries(entity.properties || {}).map(([key, value]) => (
            <ListItem key={key} divider>
              <ListItemText 
                primary={key} 
                secondary={
                  typeof value === 'object' 
                    ? JSON.stringify(value) 
                    : String(value)
                } 
              />
            </ListItem>
          ))}
          {Object.keys(entity.properties || {}).length === 0 && (
            <ListItem>
              <ListItemText primary="No properties defined" />
            </ListItem>
          )}
        </List>
      </Paper>
      
      <Typography variant="h6">Relationships</Typography>
      <Paper variant="outlined" sx={{ mt: 1, mb: 3 }}>
        <Box p={2}>
          <Typography variant="body2" color="text.secondary">
            Loading relationships...
          </Typography>
        </Box>
      </Paper>
      
      {!readOnly && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          {onEdit && (
            <Button 
              variant="outlined" 
              startIcon={<Edit />} 
              onClick={() => onEdit(entity)}
              sx={{ mr: 1 }}
            >
              Edit
            </Button>
          )}
          {onDelete && (
            <Button 
              variant="outlined" 
              color="error" 
              startIcon={<Delete />} 
              onClick={() => onDelete(entity.id)}
            >
              Delete
            </Button>
          )}
        </Box>
      )}
    </Box>
  );
};