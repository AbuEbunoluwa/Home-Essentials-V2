# Build stage (using Node for a React/Vue UI or Python for a simpler one)
FROM nginx:alpine

# Copy your custom UI files to the web server's directory
COPY ./dist /usr/share/nginx/html

# Expose port 80 for the web traffic
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
