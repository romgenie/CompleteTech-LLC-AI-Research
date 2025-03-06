const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();
const PORT = process.env.PORT || 3000;

// Get API URL from environment variable or use default
const apiUrl = process.env.API_URL || 'http://localhost:8000';

// Proxy API requests to the FastAPI backend
app.use('/api', createProxyMiddleware({
  target: apiUrl,
  changeOrigin: true,
  pathRewrite: {
    '^/api': '', // Remove /api prefix when forwarding to target
  },
  onProxyReq: (proxyReq, req, res) => {
    // Log proxy requests
    console.log(`Proxying request to: ${apiUrl}${proxyReq.path}`);
  }
}));

// Proxy auth requests to the FastAPI backend
app.use('/auth', createProxyMiddleware({
  target: apiUrl,
  changeOrigin: true,
  onProxyReq: (proxyReq, req, res) => {
    // Log proxy requests
    console.log(`Proxying auth request to: ${apiUrl}${proxyReq.path}`);
  }
}));

// Serve static files from the current directory
app.use(express.static(__dirname));

// Send the index.html for all other routes to enable SPA functionality
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`Landing page server running on port ${PORT}`);
});