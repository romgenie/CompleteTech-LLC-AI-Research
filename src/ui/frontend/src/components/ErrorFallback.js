import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Button, Paper } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

/**
 * ErrorFallback component to display error states
 * Can be used both for error boundaries and for API errors
 * 
 * @component
 */
const ErrorFallback = ({
  error,
  resetErrorBoundary,
  title = 'Error',
  message = 'An unexpected error occurred.',
  showResetButton = true,
  resetButtonText = 'Try Again',
  showErrorDetails = false,
  fullPage = false,
  icon = true
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
        height: fullPage ? '100vh' : 'auto',
        width: '100%'
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          maxWidth: '600px',
          width: '100%'
        }}
      >
        {icon && <ErrorOutlineIcon color="error" sx={{ fontSize: 60, mb: 2 }} />}
        
        <Typography variant="h5" component="h2" align="center" gutterBottom>
          {title}
        </Typography>
        
        <Typography variant="body1" align="center" color="text.secondary" paragraph>
          {message}
        </Typography>
        
        {showErrorDetails && error && (
          <Box
            sx={{
              mt: 2,
              p: 2,
              bgcolor: 'grey.100',
              borderRadius: 1,
              width: '100%',
              overflow: 'auto'
            }}
          >
            <Typography variant="subtitle2" gutterBottom>
              Error Details:
            </Typography>
            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
              {error.toString()}
            </Typography>
          </Box>
        )}
        
        {showResetButton && resetErrorBoundary && (
          <Button
            variant="contained"
            color="primary"
            onClick={resetErrorBoundary}
            sx={{ mt: 3 }}
          >
            {resetButtonText}
          </Button>
        )}
      </Paper>
    </Box>
  );
};

ErrorFallback.propTypes = {
  /** The error that occurred */
  error: PropTypes.any,
  
  /** Function to reset the error state */
  resetErrorBoundary: PropTypes.func,
  
  /** Title of the error display */
  title: PropTypes.string,
  
  /** Message explaining the error */
  message: PropTypes.string,
  
  /** Whether to show a reset button */
  showResetButton: PropTypes.bool,
  
  /** Text for the reset button */
  resetButtonText: PropTypes.string,
  
  /** Whether to show detailed error information */
  showErrorDetails: PropTypes.bool,
  
  /** Whether to make the component fill the entire viewport */
  fullPage: PropTypes.bool,
  
  /** Whether to show the error icon */
  icon: PropTypes.bool
};

export default ErrorFallback;