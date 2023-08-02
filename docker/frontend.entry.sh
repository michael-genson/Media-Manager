# Production entry point for the frontend docker container

# Web Server
caddy start --config /app/Caddyfile

# Start Application
yarn run start -p 3001
