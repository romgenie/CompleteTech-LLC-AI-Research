import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  Divider,
  Box,
  Typography,
  Chip,
  Paper,
  CircularProgress
} from '@mui/material';
import { Entity } from '../types';

interface KnowledgeGraphSearchResultsProps {
  searchResults: any[];
  selectedEntity: Entity | null;
  handleSelectEntity: (entity: Entity) => void;
  loading: boolean;
  entityColors: Record<string, string>;
}

const KnowledgeGraphSearchResults: React.FC<KnowledgeGraphSearchResultsProps> = ({
  searchResults,
  selectedEntity,
  handleSelectEntity,
  loading,
  entityColors
}) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }
  
  if (!searchResults || searchResults.length === 0) {
    return (
      <Box p={3} textAlign="center">
        <Typography variant="body1" color="text.secondary">
          Search for entities to begin exploring.
        </Typography>
      </Box>
    );
  }
  
  return (
    <List>
      {searchResults.map((entity) => (
        <React.Fragment key={entity.id}>
          <ListItem 
            button 
            onClick={() => handleSelectEntity(entity)}
            selected={selectedEntity && selectedEntity.id === entity.id}
          >
            <ListItemText 
              primary={entity.name} 
              secondary={
                <Box display="flex" alignItems="center" mt={0.5}>
                  <Chip 
                    label={entity.type} 
                    size="small" 
                    sx={{ 
                      backgroundColor: entityColors[entity.type] || entityColors.default,
                      color: 'white',
                      mr: 1
                    }} 
                  />
                  <Typography variant="caption" color="text.secondary">
                    Relevance: {entity.relevance || 'N/A'}
                  </Typography>
                </Box>
              } 
            />
          </ListItem>
          <Divider />
        </React.Fragment>
      ))}
    </List>
  );
};

export default KnowledgeGraphSearchResults;