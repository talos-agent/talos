# --------------------------------------------------------------
# Build stage
# --------------------------------------------------------------
FROM node:16-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# --------------------------------------------------------------
# Final stage
# --------------------------------------------------------------
FROM node:16-alpine

WORKDIR /app

COPY --from=builder /app .

CMD ["node", "network-scanner.js"]