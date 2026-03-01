
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY ca_desktop/frontend/package.json ca_desktop/frontend/package-lock.json ./
RUN npm ci

COPY ca_desktop/frontend/ .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
