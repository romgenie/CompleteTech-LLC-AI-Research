import React, { Component, ReactNode, ErrorInfo, ComponentType, ReactElement } from 'react';

// Define interfaces for component props and state
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactElement;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error boundary component to catch and handle errors in child components
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to console
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
    
    // Call the onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  reset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render(): ReactNode {
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

interface ErrorBoundaryOptions {
  fallback?: ReactElement;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryWrapperProps {
  children: ReactNode;
}

/**
 * Custom hook to provide an error boundary component
 * This is just a convenience hook to use the ErrorBoundary component
 * 
 * @param options - Options for the error boundary
 * @returns Error boundary component
 */
function useErrorBoundary(options: ErrorBoundaryOptions = {}): ComponentType<ErrorBoundaryWrapperProps> {
  const { fallback, onError } = options;
  
  const ErrorBoundaryWrapper: React.FC<ErrorBoundaryWrapperProps> = ({ children }) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      {children}
    </ErrorBoundary>
  );
  
  return ErrorBoundaryWrapper;
}

export { ErrorBoundary };
export default useErrorBoundary;