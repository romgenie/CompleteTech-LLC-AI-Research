import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { useWebSocket } from '../hooks';
import { useAuth } from './AuthContext';
import { 
  WebSocketMessage, 
  NotificationMessage, 
  PaperStatus, 
  WebSocketState 
} from '../types';

// Define interface for the WebSocketContext
interface WebSocketContextType {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: <T extends WebSocketMessage>(data: T) => boolean;
  lastMessage: WebSocketMessage | null;
  error: Event | null;
  notifications: NotificationMessage[];
  clearNotifications: () => void;
  removeNotification: (notificationId: string) => void;
  subscribeToPaperUpdates: (paperId: string) => boolean;
  unsubscribeFromPaperUpdates: (paperId: string) => boolean;
  paperStatusMap: Record<string, PaperStatus>;
}

// Create context with default values
const WebSocketContext = createContext<WebSocketContextType | null>(null);

interface WebSocketProviderProps {
  children: ReactNode;
}

/**
 * WebSocket Provider component for handling WebSocket connections
 */
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [paperStatusMap, setPaperStatusMap] = useState<Record<string, PaperStatus>>({});
  const notificationsRef = useRef<NotificationMessage[]>([]);
  
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
    onMessage: (data: WebSocketMessage) => {
      // Handle different message types
      if (data.type === 'notification') {
        const notificationData = data as NotificationMessage;
        const newNotifications = [...notificationsRef.current, notificationData];
        setNotifications(newNotifications);
        notificationsRef.current = newNotifications;
      } else if (data.type === 'paper_status') {
        // Update paper status map
        setPaperStatusMap(prev => ({
          ...prev,
          [data.paperId]: data.status as PaperStatus
        }));
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
  const subscribeToPaperUpdates = (paperId: string): boolean => {
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
  const unsubscribeFromPaperUpdates = (paperId: string): boolean => {
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
  const clearNotifications = (): void => {
    setNotifications([]);
    notificationsRef.current = [];
  };
  
  // Remove a specific notification
  const removeNotification = (notificationId: string): void => {
    const updatedNotifications = notificationsRef.current.filter(
      n => n.id !== notificationId
    );
    setNotifications(updatedNotifications);
    notificationsRef.current = updatedNotifications;
  };
  
  // Context value
  const contextValue: WebSocketContextType = {
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
    unsubscribeFromPaperUpdates,
    paperStatusMap
  };
  
  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

/**
 * Custom hook for using WebSocket context
 * @returns WebSocket context value
 */
export const useWebSocketContext = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;