# Stage 1: Build the application
FROM node:18-alpine AS builder

# Set working directory to the root of the monorepo within the container
WORKDIR /app

# Install pnpm and turbo globally (using the versions from your package.json)
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Debug: List the contents of the build context root provided by Railway
RUN echo "--- Listing build context root ---" && ls -la .

# Copy all monorepo manifest files.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json .npmrc ./
# The trailing './' ensures it copies into the WORKDIR.
# This command assumes .npmrc exists. If not, remove it from the list.

# Copy all source code
COPY apps ./apps
COPY packages ./packages

# Install all monorepo dependencies. This must run after manifests and source code are copied.
RUN pnpm install --frozen-lockfile

# Build the specific 'web' application. This uses the turbo.json pipeline.
RUN turbo run build --filter=web

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
# This includes node_modules and the server.js file.
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets from the builder stage
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static

EXPOSE 3000

# The command to run the Next.js standalone server
CMD ["node", "server.js"] 