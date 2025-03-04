import React from 'react';
import PropTypes from 'prop-types';
import { Box, CircularProgress, Typography } from '@mui/material';

/**
 * LoadingFallback component to display a loading indicator
 * Used for Suspense fallback and loading states
 * 
 * @component
 */
const LoadingFallback = ({
  message = 'Loading...',
  fullPage = false,
  height = '200px',
  minHeight = null,
  showSpinner = true,
  spinnerSize = 40
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        height: fullPage ? '100vh' : height,
        minHeight: minHeight,
        p: 3
      }}
    >
      {showSpinner && (
        <CircularProgress 
          size={spinnerSize} 
          thickness={4} 
          color="primary" 
          sx={{ mb: 2 }}
        />
      )}
      
      {message && (
        <Typography 
          variant="body1" 
          color="text.secondary"
          align="center"
        >
          {message}
        </Typography>
      )}
    </Box>
  );
};

LoadingFallback.propTypes = {
  /** Message to display below the spinner */
  message: PropTypes.string,
  
  /** Whether to make the component fill the entire viewport */
  fullPage: PropTypes.bool,
  
  /** Height of the component (when not fullPage) */
  height: PropTypes.string,
  
  /** Minimum height of the component */
  minHeight: PropTypes.string,
  
  /** Whether to show the spinner */
  showSpinner: PropTypes.bool,
  
  /** Size of the spinner in pixels */
  spinnerSize: PropTypes.number
};

export default LoadingFallback;