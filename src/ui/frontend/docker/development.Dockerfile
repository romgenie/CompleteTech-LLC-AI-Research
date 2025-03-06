FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy all files
COPY . .

# Set environment variables
ENV PORT=3001
ENV REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws

# Expose port 3001
EXPOSE 3001

# Start development server
CMD ["npm", "start"]