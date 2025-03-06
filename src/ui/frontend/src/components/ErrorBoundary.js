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
          reset: this.handleReset
        });
      }

      // Default fallback UI
      return (
        <Box 
          sx={{
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            bgcolor: 'background.paper',
            borderRadius: 1
          }}
        >
          <ErrorOutlineIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h5" component="h2" gutterBottom>
            {errorTitle}
          </Typography>
          
          {process.env.NODE_ENV === 'development' && (
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                mt: 2, 
                width: '100%', 
                overflow: 'auto', 
                maxHeight: '300px' 
              }}
            >
              <Typography variant="subtitle2" gutterBottom>
                Error Details:
              </Typography>
              <Typography variant="body2" component="pre" sx={{ fontSize: '0.8rem' }}>
                {error && error.toString()}
              </Typography>
              
              {errorInfo && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Component Stack:
                  </Typography>
                  <Typography variant="body2" component="pre" sx={{ fontSize: '0.8rem' }}>
                    {errorInfo.componentStack}
                  </Typography>
                </>
              )}
            </Paper>
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
        </Box>
      );
    }

    // No error, render children
    return children;
  }
}

ErrorBoundary.propTypes = {
  /** Children to render when there's no error */
  children: PropTypes.node.isRequired,
  
  /** Custom component to render when an error occurs */
  fallback: PropTypes.element,
  
  /** Whether to show reset button */
  showReset: PropTypes.bool,
  
  /** Text for reset button */
  resetButtonText: PropTypes.string,
  
  /** Title for the error message */
  errorTitle: PropTypes.string,
  
  /** Callback function when an error occurs */
  onError: PropTypes.func,
  
  /** Callback function when reset button is clicked */
  onReset: PropTypes.func
};

export default ErrorBoundary;