# Stage 1: Build
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Serve with Node
FROM node:22-alpine

WORKDIR /app
COPY --from=builder /app/dist ./dist
RUN npm install -g serve

EXPOSE 80

CMD ["serve", "-s", "dist", "-l", "80"]
