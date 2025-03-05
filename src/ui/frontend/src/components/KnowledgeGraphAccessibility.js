import React from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText } from '@mui/material';

/**
 * Component for accessibility features for the Knowledge Graph
 */
const KnowledgeGraphAccessibility = ({ 
  selectedEntity, 
  relatedEntities, 
  handleSelectEntity,
  zoomLevel
}) => {
  return (
    <Paper elevation={3} sx={{ p: 2, mb: 2, maxHeight: '300px', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Accessibility Information
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2">Keyboard Navigation</Typography>
        <List dense>
          <ListItem>
            <ListItemText 
              primary="Arrow Keys" 
              secondary="Navigate between connected nodes" 
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="Enter" 
              secondary="Select the currently focused node" 
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="+ / -" 
              secondary="Zoom in and out of the graph" 
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="Home" 
              secondary="Reset zoom and center graph" 
            />
          </ListItem>
        </List>
      </Box>
      
      {selectedEntity && (
        <Box>
          <Typography variant="subtitle2">Current Selection</Typography>
          <Typography variant="body2">
            {`${selectedEntity.type}: ${selectedEntity.name}`}
          </Typography>
          
          {relatedEntities && relatedEntities.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="subtitle2">Connected Entities</Typography>
              <List dense>
                {relatedEntities.slice(0, 5).map(entity => (
                  <ListItem 
                    key={entity.id} 
                    button 
                    onClick={() => handleSelectEntity(entity)}
                  >
                    <ListItemText
                      primary={entity.name}
                      secondary={`${entity.type}`}
                    />
                  </ListItem>
                ))}
                {relatedEntities.length > 5 && (
                  <ListItem>
                    <ListItemText
                      secondary={`${relatedEntities.length - 5} more connected entities...`}
                    />
                  </ListItem>
                )}
              </List>
            </Box>
          )}
        </Box>
      )}
      
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2">Current View</Typography>
        <Typography variant="body2">
          {`Zoom level: ${Math.round(zoomLevel * 100)}%`}
        </Typography>
      </Box>
    </Paper>
  );
};

export default KnowledgeGraphAccessibility;