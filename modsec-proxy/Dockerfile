FROM owasp/modsecurity-crs:nginx

# Copy Nginx configuration file to override default template
COPY default.conf.template /etc/nginx/templates/conf.d/default.conf.template

# Expose port 8080 (same as the app)
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]