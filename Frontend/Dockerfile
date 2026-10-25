# Stage 1: Build
ARG NODE_IMAGE=node:22-bookworm-slim
FROM ${NODE_IMAGE} AS builder

# Install build dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
# Use npm install because this repo does not include package-lock.json in production builds.
RUN npm install --legacy-peer-deps

COPY . .
RUN npx nuxt build

# Stage 2: Runtime
FROM ${NODE_IMAGE}

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
