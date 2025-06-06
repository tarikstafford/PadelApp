# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Install pnpm and turbo globally
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy all monorepo manifest files from their specific locations
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json .npmrc ./
# This assumes .npmrc exists at the monorepo root. If not, remove it.

# Copy all source code
COPY apps ./apps
COPY packages ./packages

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Build the specific 'web' application
RUN turbo run build --filter=web

# After build, list the contents of the standalone directory for debugging
RUN ls -R /app/apps/web/.next/standalone

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the entire standalone output into /app
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets to the correct location
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static

EXPOSE 3000

# CORRECTED: Use the full, correct path to server.js inside the standalone output
CMD ["node", "apps/web/server.js"] 