# Stage 1: Build
FROM node:20-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
# Use npm ci for a cleaner install in CI
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-slim

WORKDIR /app

# Install production dependencies for runtime if needed (usually not for nuxt .output)
# But let's keep it minimal

# Copy output from builder
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package*.json ./

# Set environment
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# Security: Run as non-root user
RUN groupadd -r nodejs && useradd -r -g nodejs nodejs && \
    chown -R nodejs:nodejs /app
USER nodejs

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
