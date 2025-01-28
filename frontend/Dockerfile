FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Create environment file
RUN echo "VITE_API_URL=${VITE_API_URL}" > .env

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Set environment variable for nginx template
ENV VITE_API_URL=${VITE_API_URL}

# Use shell script to replace environment variables in nginx config
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]