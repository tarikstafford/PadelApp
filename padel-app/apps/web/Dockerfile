# Stage 1: Build the application
FROM node:18-alpine AS builder

# Set working directory to the root of the monorepo within the container
WORKDIR /app

# Install pnpm and turbo globally (using the versions from your package.json)
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy all source code, respecting the .dockerignore at the monorepo root
COPY . .

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Build the specific 'web' application
RUN turbo run build --filter=web

# Stage 2: Production Image
# Use a minimal Node.js image for the final production stage
FROM node:18-alpine AS production-runner

WORKDIR /app

# Set the environment to production
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets from the builder stage
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static

# The standalone output includes a copy of the 'public' folder, so we don't need a separate COPY for it.

# Expose the port Next.js will run on
EXPOSE 3000

# The command to run the Next.js standalone server
CMD ["node", "server.js"] 