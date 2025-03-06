import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Divider,
  Paper,
  Grid,
  CircularProgress
} from '@mui/material';
import { Entity } from '../types';

interface EntityDetails extends Entity {
  description?: string;
  properties?: Record<string, any>;
}

interface KnowledgeGraphEntityDetailsProps {
  selectedEntity: Entity | null;
  entityDetails: EntityDetails | null;
  loading: boolean;
  entityColors: Record<string, string>;
}

const KnowledgeGraphEntityDetails: React.FC<KnowledgeGraphEntityDetailsProps> = ({
  selectedEntity,
  entityDetails,
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
  
  if (!selectedEntity) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <Typography variant="body1" color="text.secondary">
          Select an entity to view details
        </Typography>
      </Box>
    );
  }
  
  if (!entityDetails) {
    return (
      <Typography variant="body1" align="center">No details available</Typography>
    );
  }
  
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'medium' }}>
          {entityDetails.name}
        </Typography>
        <Chip 
          label={entityDetails.type} 
          size="medium" 
          sx={{
            backgroundColor: entityColors[entityDetails.type] || entityColors.default,
            color: 'white',
            fontWeight: 'bold',
            paddingX: 1
          }}
        />
      </Box>
      
      <Divider sx={{ my: 2 }} />
      
      <Box sx={{ maxHeight: '18vh', overflowY: 'auto', pr: 1 }}>
        <Grid container spacing={2}>
          {entityDetails.properties && Object.entries(entityDetails.properties).map(([key, value]) => (
            <Grid item xs={12} sm={6} key={key}>
              <Paper 
                variant="outlined" 
                sx={{ 
                  p: 1, 
                  display: 'flex', 
                  flexDirection: 'column',
                  height: '100%',
                  bgcolor: 'background.default'
                }}
              >
                <Typography 
                  variant="caption" 
                  color="text.secondary" 
                  component="div"
                  sx={{ textTransform: 'uppercase', fontWeight: 'bold', fontSize: '0.65rem' }}
                >
                  {key}
                </Typography>
                <Typography 
                  variant="body2" 
                  component="div" 
                  sx={{ 
                    fontWeight: key === 'citations' || key === 'complexity' ? 'medium' : 'regular',
                    color: key === 'citations' ? 'success.main' : 'text.primary'
                  }}
                >
                  {value?.toString()}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
        
        {entityDetails.description && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
              {entityDetails.description}
            </Typography>
          </>
        )}
      </Box>
    </Box>
  );
};

export default KnowledgeGraphEntityDetails;