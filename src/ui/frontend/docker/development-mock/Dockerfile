FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json ./

# Install dependencies
RUN npm install

# Copy mock API server code
COPY api.js ./

# Expose port 8000
EXPOSE 8000

# Start the mock API server
CMD ["node", "api.js"]