import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Button, Paper, Divider } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

/**
 * Error Boundary component for catching and gracefully handling React errors
 * 
 * @component
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by ErrorBoundary:', error, errorInfo);
    }
    
    this.setState({ errorInfo });
    
    // Call the onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  /**
   * Reset the error state to recover from the error
   */
  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
    
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { 
      children, 
      fallback,
      showReset = true,
      resetButtonText = 'Try Again',
      errorTitle = 'Something went wrong'
    } = this.props;

    if (hasError) {
      // Check if a custom fallback component was provided
      if (fallback) {
        return React.cloneElement(fallback, {
          error,
          errorInfo,
          reset: this.handleReset
        });
      }

      // Default fallback UI
      return (
        <Box 
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
            m: 2,
            maxWidth: '100%'
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
            <ErrorOutlineIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
            
            <Typography variant="h5" component="h2" align="center" gutterBottom>
              {errorTitle}
            </Typography>
            
            <Typography variant="body1" align="center" color="text.secondary" paragraph>
              An unexpected error occurred in the application. 
              {showReset && " Please try again or contact support if the problem persists."}
            </Typography>
            
            {process.env.NODE_ENV === 'development' && (
              <>
                <Divider sx={{ width: '100%', my: 2 }} />
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
                    Error Details (Development Only):
                  </Typography>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {error && error.toString()}
                  </Typography>
                  {errorInfo && (
                    <Typography variant="body2" component="pre" sx={{ mt: 2, whiteSpace: 'pre-wrap' }}>
                      {errorInfo.componentStack}
                    </Typography>
                  )}
                </Box>
              </>
            )}
            
            {showReset && (
              <Button 
                variant="contained" 
                color="primary" 
                onClick={this.handleReset}
                sx={{ mt: 3 }}
              >
                {resetButtonText}
              </Button>
            )}
          </Paper>
        </Box>
      );
    }

    return children;
  }
}

ErrorBoundary.propTypes = {
  /** Content to render when no error is present */
  children: PropTypes.node.isRequired,
  
  /** Custom component to render when an error occurs */
  fallback: PropTypes.element,
  
  /** Callback function when an error occurs */
  onError: PropTypes.func,
  
  /** Callback function when reset is triggered */
  onReset: PropTypes.func,
  
  /** Whether to show the reset button */
  showReset: PropTypes.bool,
  
  /** Text for the reset button */
  resetButtonText: PropTypes.string,
  
  /** Title text for the error message */
  errorTitle: PropTypes.string
};

export default ErrorBoundary;