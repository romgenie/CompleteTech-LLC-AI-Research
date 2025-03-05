import React from 'react';
import { Box, Typography, Button, Container, Paper } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';

/**
 * NotFound page component for 404 errors
 */
const NotFound = () => {
  return (
    <Container maxWidth="md">
      <Paper sx={{ 
        p: 5, 
        mt: 5, 
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <Typography variant="h1" component="h1" sx={{ fontSize: '6rem', color: 'primary.main' }}>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          The page you are looking for does not exist or has been moved.
        </Typography>
        <Button 
          component={RouterLink} 
          to="/" 
          variant="contained" 
          startIcon={<HomeIcon />}
          size="large"
          sx={{ mt: 2 }}
        >
          Back to Home
        </Button>
      </Paper>
    </Container>
  );
};

export default NotFound;