import React, { Component } from 'react';
import PropTypes from 'prop-types';

/**
 * Error boundary component to catch and handle errors in child components
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
    // Log the error to console
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
    
    // Call the onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  reset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { fallback, children } = this.props;

    if (hasError) {
      // Check if a custom fallback component was provided
      if (fallback) {
        return React.cloneElement(fallback, {
          error,
          errorInfo,
          reset: this.reset
        });
      }

      // Default fallback UI
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <button onClick={this.reset}>Try again</button>
          {process.env.NODE_ENV === 'development' && (
            <details style={{ whiteSpace: 'pre-wrap', marginTop: '16px' }}>
              <summary>Error details</summary>
              {error && error.toString()}
              <br />
              {errorInfo && errorInfo.componentStack}
            </details>
          )}
        </div>
      );
    }

    return children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.element,
  onError: PropTypes.func
};

/**
 * Custom hook to provide an error boundary component
 * This is just a convenience hook to use the ErrorBoundary component
 * 
 * @param {Object} options - Options for the error boundary
 * @param {React.Element} options.fallback - Custom fallback component
 * @param {Function} options.onError - Error callback function
 * @returns {Component} - Error boundary component
 */
function useErrorBoundary(options = {}) {
  const { fallback, onError } = options;
  
  const ErrorBoundaryWrapper = ({ children }) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      {children}
    </ErrorBoundary>
  );
  
  ErrorBoundaryWrapper.propTypes = {
    children: PropTypes.node.isRequired
  };
  
  return ErrorBoundaryWrapper;
}

export { ErrorBoundary };
export default useErrorBoundary;