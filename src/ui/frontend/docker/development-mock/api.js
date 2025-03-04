/**
 * Mock API server for frontend development
 * 
 * This Express server provides mock endpoints that mimic the backend API
 * for development purposes when the actual backend is not available.
 */

const express = require('express');
const cors = require('cors');
const http = require('http');
const { WebSocketServer } = require('ws');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');

// Mock data
const mockData = require('./mockData.js');

// Create Express app
const app = express();
const port = 8000;

// Create HTTP server
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ server, path: '/ws' });

// Configure middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// JWT Secret
const JWT_SECRET = 'mock-secret-key';

// Helper function to create JWT token
const createToken = (user) => {
  return jwt.sign(
    {
      sub: user.id.toString(),
      username: user.username,
      role: user.role,
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
    },
    JWT_SECRET
  );
};

// Middleware to verify JWT token
const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ detail: 'Unauthorized' });
  }
  
  const token = authHeader.split(' ')[1];
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ detail: 'Invalid token' });
  }
};

// Auth routes
app.post('/auth/token', (req, res) => {
  const { username, password } = req.body;
  
  // Check if user exists in mock data
  const user = {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: 'Admin User',
    role: 'admin',
    permissions: ['read', 'write', 'admin']
  };
  
  if (username === 'admin' && password === 'password') {
    const token = createToken(user);
    
    res.json({
      access_token: token,
      token_type: 'bearer',
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    });
  } else {
    res.status(401).json({ detail: 'Invalid username or password' });
  }
});

app.get('/auth/users/me', verifyToken, (req, res) => {
  // Return user info based on token
  res.json({
    id: req.user.sub,
    username: req.user.username,
    email: `${req.user.username}@example.com`,
    full_name: `${req.user.username.charAt(0).toUpperCase() + req.user.username.slice(1)} User`,
    role: req.user.role,
    permissions: ['read', 'write', req.user.role === 'admin' ? 'admin' : ''].filter(Boolean)
  });
});

// Paper routes
app.get('/api/papers', verifyToken, (req, res) => {
  res.json(mockData.papers);
});

app.get('/api/papers/recent', verifyToken, (req, res) => {
  const recentPapers = mockData.papers.slice(0, 5);
  res.json(recentPapers);
});

app.get('/api/papers/:id', verifyToken, (req, res) => {
  const paper = mockData.papers.find(p => p.id === req.params.id);
  
  if (paper) {
    res.json(paper);
  } else {
    res.status(404).json({ detail: 'Paper not found' });
  }
});

app.post('/api/papers', verifyToken, (req, res) => {
  const { title, authors, year, abstract } = req.body;
  
  // Validate required fields
  if (!title || !authors) {
    return res.status(400).json({ detail: 'Title and authors are required' });
  }
  
  // Create new paper with mock ID
  const newPaper = {
    id: `paper-${Date.now()}`,
    title,
    authors: typeof authors === 'string' ? authors.split(',').map(a => a.trim()) : authors,
    year: year || new Date().getFullYear().toString(),
    abstract: abstract || '',
    status: 'uploaded',
    uploaded_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    url: `https://example.com/papers/${Date.now()}`
  };
  
  // In a real API, we would save this to a database
  // For mock, we'll just return the created paper
  res.status(201).json(newPaper);
});

// Knowledge Graph routes
app.get('/api/knowledge-graph', verifyToken, (req, res) => {
  res.json(mockData.knowledgeGraph);
});

app.get('/api/knowledge-graph/paper/:id', verifyToken, (req, res) => {
  // For mock, we'll just return the same graph for any paper ID
  res.json(mockData.knowledgeGraph);
});

// Research routes
app.post('/api/research/query', verifyToken, (req, res) => {
  const { query, sources, options } = req.body;
  
  // Validate required fields
  if (!query) {
    return res.status(400).json({ detail: 'Query is required' });
  }
  
  // For mock, we'll just return the same results for any query
  res.json(mockData.researchResults);
});

// Implementation routes
app.get('/api/implementation/paper/:id', verifyToken, (req, res) => {
  // For mock, we'll just return the same implementation for any paper ID
  res.json(mockData.implementation);
});

// WebSocket connections
wss.on('connection', (ws) => {
  console.log('Client connected to WebSocket');
  
  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connection_established',
    message: 'Connected to mock WebSocket server',
    timestamp: new Date().toISOString()
  }));
  
  // Handle messages from the client
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      
      // Handle authentication
      if (data.type === 'auth') {
        try {
          const decoded = jwt.verify(data.token, JWT_SECRET);
          console.log('WebSocket authenticated:', decoded.username);
          
          // Send success message
          ws.send(JSON.stringify({
            type: 'auth_success',
            user: decoded.username,
            timestamp: new Date().toISOString()
          }));
          
          // Send mock notification after 2 seconds
          setTimeout(() => {
            ws.send(JSON.stringify({
              id: `notification-${Date.now()}`,
              type: 'notification',
              category: 'success',
              title: 'Authentication Successful',
              message: `Welcome, ${decoded.username}! You are now receiving real-time updates.`,
              timestamp: new Date().toISOString()
            }));
          }, 2000);
        } catch (err) {
          ws.send(JSON.stringify({
            type: 'auth_error',
            error: 'Invalid token',
            timestamp: new Date().toISOString()
          }));
        }
      }
      
      // Handle paper status subscriptions
      if (data.type === 'subscribe' && data.channel.startsWith('paper_status_')) {
        const paperId = data.channel.replace('paper_status_', '');
        console.log(`Subscribed to paper status: ${paperId}`);
        
        // Confirm subscription
        ws.send(JSON.stringify({
          type: 'subscription_success',
          channel: data.channel,
          timestamp: new Date().toISOString()
        }));
        
        // Send mock status updates every 5 seconds
        const statusInterval = setInterval(() => {
          const statuses = [
            'queued',
            'processing',
            'extracting_entities',
            'extracting_relationships',
            'building_knowledge_graph',
            'analyzed',
            'implementation_ready'
          ];
          
          const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
          
          ws.send(JSON.stringify({
            type: 'paper_status_update',
            paper_id: paperId,
            status: randomStatus,
            timestamp: new Date().toISOString()
          }));
        }, 5000);
        
        // Store interval ID to clear on unsubscribe
        ws.statusIntervals = ws.statusIntervals || {};
        ws.statusIntervals[paperId] = statusInterval;
      }
      
      // Handle unsubscribe
      if (data.type === 'unsubscribe' && data.channel.startsWith('paper_status_')) {
        const paperId = data.channel.replace('paper_status_', '');
        console.log(`Unsubscribed from paper status: ${paperId}`);
        
        // Clear interval
        if (ws.statusIntervals && ws.statusIntervals[paperId]) {
          clearInterval(ws.statusIntervals[paperId]);
          delete ws.statusIntervals[paperId];
        }
        
        // Confirm unsubscription
        ws.send(JSON.stringify({
          type: 'unsubscription_success',
          channel: data.channel,
          timestamp: new Date().toISOString()
        }));
      }
    } catch (err) {
      console.error('Error processing WebSocket message:', err);
      ws.send(JSON.stringify({
        type: 'error',
        error: 'Invalid message format',
        timestamp: new Date().toISOString()
      }));
    }
  });
  
  // Handle client disconnect
  ws.on('close', () => {
    console.log('Client disconnected from WebSocket');
    
    // Clean up any intervals
    if (ws.statusIntervals) {
      Object.values(ws.statusIntervals).forEach(interval => clearInterval(interval));
    }
  });
  
  // Send a notification every 30 seconds
  const notificationInterval = setInterval(() => {
    const categories = ['info', 'success', 'warning', 'error', 'paper_status'];
    const randomCategory = categories[Math.floor(Math.random() * categories.length)];
    
    const titles = {
      info: 'Information Update',
      success: 'Operation Successful',
      warning: 'Warning',
      error: 'Error Occurred',
      paper_status: 'Paper Status Update'
    };
    
    const messages = {
      info: 'New research data is available for analysis.',
      success: 'Your request has been processed successfully.',
      warning: 'Some features may be unavailable due to maintenance.',
      error: 'Unable to connect to the knowledge graph database.',
      paper_status: 'A paper has been processed and is ready for implementation.'
    };
    
    ws.send(JSON.stringify({
      id: `notification-${Date.now()}`,
      type: 'notification',
      category: randomCategory,
      title: titles[randomCategory],
      message: messages[randomCategory],
      timestamp: new Date().toISOString(),
      action: randomCategory === 'paper_status' ? {
        type: 'navigate',
        path: '/implementation'
      } : null
    }));
  }, 30000);
  
  // Clean up on disconnect
  ws.on('close', () => {
    clearInterval(notificationInterval);
  });
});

// Start the server
server.listen(port, () => {
  console.log(`Mock API server running at http://localhost:${port}`);
  console.log(`WebSocket server running at ws://localhost:${port}/ws`);
});