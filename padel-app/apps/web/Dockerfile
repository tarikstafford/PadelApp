# Stage 1: Build the application
FROM node:18-alpine AS builder
WORKDIR /app

# Per Railway docs, declare the ARG in the stage it is required.
ARG NEXT_PUBLIC_API_URL
# Expose the build argument as an environment variable for the build stage.
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Install pnpm and turbo globally
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy all source code from the build context
# The .dockerignore file at the root will prevent copying node_modules, .turbo, .git, etc.
COPY . .

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Build the specific 'web' application
# This command needs the full monorepo context to work correctly
RUN turbo run build --filter=web

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets from the builder stage
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static

EXPOSE 3000

# CORRECTED: Use the full, correct path to server.js inside the standalone output
CMD ["node", "apps/web/server.js"] 