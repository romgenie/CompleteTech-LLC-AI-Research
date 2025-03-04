import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useWebSocket } from '../hooks';
import { useAuth } from './AuthContext';

// Create WebSocket context
const WebSocketContext = createContext(null);

/**
 * WebSocket Provider component for handling WebSocket connections
 * 
 * @component
 */
export const WebSocketProvider = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const notificationsRef = useRef([]);
  
  // Construct WebSocket URL based on current location
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = process.env.REACT_APP_WEBSOCKET_HOST || window.location.host;
  const wsUrl = `${protocol}//${host}/ws`;
  
  // Initialize WebSocket with auth token
  const {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    lastMessage,
    error
  } = useWebSocket(wsUrl, {
    autoConnect: false,
    onMessage: (data) => {
      if (data.type === 'notification') {
        const newNotifications = [...notificationsRef.current, data];
        setNotifications(newNotifications);
        notificationsRef.current = newNotifications;
      }
    }
  });
  
  // Connect when authenticated and disconnect when not
  useEffect(() => {
    if (isAuthenticated && token) {
      // Add token to connection for authentication
      connect();
    } else {
      disconnect();
    }
    
    return () => {
      disconnect();
    };
  }, [isAuthenticated, token, connect, disconnect]);
  
  // Send authentication message after connection is established
  useEffect(() => {
    if (isAuthenticated && token && isConnected) {
      sendMessage({ type: 'auth', token });
    }
  }, [isAuthenticated, token, isConnected, sendMessage]);
  
  // Handle paper status updates
  const subscribeToPaperUpdates = (paperId) => {
    if (isConnected) {
      sendMessage({ 
        type: 'subscribe', 
        channel: `paper_status_${paperId}` 
      });
      return true;
    }
    return false;
  };
  
  // Unsubscribe from paper updates
  const unsubscribeFromPaperUpdates = (paperId) => {
    if (isConnected) {
      sendMessage({ 
        type: 'unsubscribe', 
        channel: `paper_status_${paperId}` 
      });
      return true;
    }
    return false;
  };
  
  // Clear notifications
  const clearNotifications = () => {
    setNotifications([]);
    notificationsRef.current = [];
  };
  
  // Remove a specific notification
  const removeNotification = (notificationId) => {
    const updatedNotifications = notificationsRef.current.filter(
      n => n.id !== notificationId
    );
    setNotifications(updatedNotifications);
    notificationsRef.current = updatedNotifications;
  };
  
  // Context value
  const contextValue = {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    lastMessage,
    error,
    notifications,
    clearNotifications,
    removeNotification,
    subscribeToPaperUpdates,
    unsubscribeFromPaperUpdates
  };
  
  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

/**
 * Custom hook for using WebSocket context
 * 
 * @returns {Object} WebSocket context value
 */
export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;