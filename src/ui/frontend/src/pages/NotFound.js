import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper
} from '@mui/material';
import { Error as ErrorIcon } from '@mui/icons-material';

/**
 * 404 Not Found page component
 */
const NotFound = () => {
  return (
    <Container maxWidth="md">
      <Paper 
        sx={{ 
          p: 6,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center'
        }}
      >
        <ErrorIcon 
          color="error" 
          sx={{ fontSize: 64, mb: 2 }} 
        />
        
        <Typography variant="h3" component="h1" gutterBottom>
          404: Page Not Found
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph>
          The page you are looking for might have been removed, had its name changed,
          or is temporarily unavailable.
        </Typography>
        
        <Box sx={{ mt: 4 }}>
          <Button
            component={RouterLink}
            to="/workspaces"
            variant="contained"
            size="large"
          >
            Return to Workspaces
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;