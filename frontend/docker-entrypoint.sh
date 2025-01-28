#!/bin/sh

# Replace environment variables in nginx config
envsubst '${VITE_API_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute CMD
exec "$@" 