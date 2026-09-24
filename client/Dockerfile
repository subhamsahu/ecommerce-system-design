# Stage 1: Build
FROM node:22-alpine AS builder

WORKDIR /app

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve static assets with the existing Node-based static server.
FROM node:22-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
RUN npm install -g serve

EXPOSE 80

CMD ["serve", "-s", "dist", "-l", "80"]
