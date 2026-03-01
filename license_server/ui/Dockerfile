
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

COPY license_server/ui/package.json license_server/ui/package-lock.json ./
RUN npm ci

COPY license_server/ui/ .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
