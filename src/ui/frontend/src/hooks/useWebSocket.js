import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for WebSocket connections with reconnection capability
 * 
 * @param {string} url - The WebSocket URL to connect to
 * @param {Object} options - Configuration options
 * @param {boolean} options.autoConnect - Whether to connect automatically (default: true)
 * @param {number} options.reconnectInterval - Interval in ms between reconnection attempts (default: 2000)
 * @param {number} options.maxReconnectAttempts - Maximum number of reconnection attempts (default: 5)
 * @param {Function} options.onMessage - Callback function for incoming messages
 * @param {Function} options.onOpen - Callback function when connection opens
 * @param {Function} options.onClose - Callback function when connection closes
 * @param {Function} options.onError - Callback function on connection error
 * @returns {Object} - WebSocket state and control functions
 */
function useWebSocket(url, options = {}) {
  const {
    autoConnect = true,
    reconnectInterval = 2000,
    maxReconnectAttempts = 5,
    onMessage = () => {},
    onOpen = () => {},
    onClose = () => {},
    onError = () => {}
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [reconnectCount, setReconnectCount] = useState(0);
  const [error, setError] = useState(null);
  
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Connect to WebSocket
  const connect = useCallback(() => {
    // Clean up existing connection
    if (socketRef.current) {
      socketRef.current.close();
    }
    
    // Clear any existing reconnect timeouts
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    try {
      const socket = new WebSocket(url);
      socketRef.current = socket;
      
      socket.onopen = (event) => {
        setIsConnected(true);
        setReconnectCount(0);
        setError(null);
        onOpen(event);
      };
      
      socket.onmessage = (event) => {
        let data;
        try {
          data = JSON.parse(event.data);
        } catch (e) {
          data = event.data;
        }
        
        setMessages(prev => [...prev, data]);
        onMessage(data, event);
      };
      
      socket.onclose = (event) => {
        setIsConnected(false);
        onClose(event);
        
        // Attempt to reconnect if this wasn't a normal closure and we haven't exceeded max attempts
        if (!event.wasClean && reconnectCount < maxReconnectAttempts) {
          setReconnectCount(prev => prev + 1);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
      
      socket.onerror = (event) => {
        setError(event);
        onError(event);
      };
    } catch (err) {
      setError(err);
      onError(err);
    }
  }, [url, reconnectCount, maxReconnectAttempts, reconnectInterval, onMessage, onOpen, onClose, onError]);
  
  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    setIsConnected(false);
  }, []);
  
  // Send message to WebSocket
  const sendMessage = useCallback((data) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message = typeof data === 'object' ? JSON.stringify(data) : data;
      socketRef.current.send(message);
      return true;
    }
    return false;
  }, []);
  
  // Connect on mount if autoConnect is true
  useEffect(() => {
    if (autoConnect) {
      connect();
    }
    
    // Clean up on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);
  
  return {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    messages,
    lastMessage: messages.length > 0 ? messages[messages.length - 1] : null,
    reconnectCount,
    error
  };
}

export default useWebSocket;