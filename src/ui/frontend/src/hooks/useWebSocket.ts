import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage, WebSocketOptions } from '../types';

interface UseWebSocketResult {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: <T extends WebSocketMessage>(data: T) => boolean;
  messages: WebSocketMessage[];
  lastMessage: WebSocketMessage | null;
  reconnectCount: number;
  error: Event | null;
}

/**
 * Custom hook for WebSocket connections with reconnection capability
 * 
 * @param url - The WebSocket URL to connect to
 * @param options - Configuration options
 * @returns WebSocket state and control functions
 */
function useWebSocket(
  url: string, 
  options: WebSocketOptions = {}
): UseWebSocketResult {
  const {
    autoConnect = true,
    reconnectInterval = 2000,
    maxReconnectAttempts = 5,
    onMessage = () => {},
    onOpen = () => {},
    onClose = () => {},
    onError = () => {}
  } = options;

  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [reconnectCount, setReconnectCount] = useState<number>(0);
  const [error, setError] = useState<Event | null>(null);
  
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

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
      
      socket.onopen = (event: Event) => {
        setIsConnected(true);
        setReconnectCount(0);
        setError(null);
        onOpen(event);
      };
      
      socket.onmessage = (event: MessageEvent) => {
        let data: WebSocketMessage;
        try {
          data = JSON.parse(event.data) as WebSocketMessage;
        } catch (e) {
          data = { type: 'raw', data: event.data };
        }
        
        setMessages(prev => [...prev, data]);
        onMessage(data, event);
      };
      
      socket.onclose = (event: CloseEvent) => {
        setIsConnected(false);
        onClose(event);
        
        // Attempt to reconnect if this wasn't a normal closure and we haven't exceeded max attempts
        if (!event.wasClean && reconnectCount < maxReconnectAttempts) {
          setReconnectCount(prev => prev + 1);
          
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
      
      socket.onerror = (event: Event) => {
        setError(event);
        onError(event);
      };
    } catch (err) {
      const error = err instanceof Event ? err : new Event('error');
      setError(error);
      onError(error);
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
  const sendMessage = useCallback(<T extends WebSocketMessage>(data: T): boolean => {
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