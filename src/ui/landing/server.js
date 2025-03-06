const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the current directory
app.use(express.static(__dirname));

// Send the index.html for all routes to enable SPA functionality
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'index.html'));
});

// Proxy API requests to the FastAPI backend
app.use('/api', (req, res) => {
  // This is a placeholder - in production you would use http-proxy-middleware
  // to properly proxy requests to your API backend
  res.redirect('http://localhost:8000' + req.url);
});

// Start the server
app.listen(PORT, () => {
  console.log(`Landing page server running on port ${PORT}`);
});