# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Install pnpm and turbo globally
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy all source code from the build context
# The .dockerignore file at the root will prevent copying node_modules, .turbo, .git, etc.
COPY . .

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Build the specific 'web' application
RUN turbo run build --filter=web

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
# This includes the server.js and a node_modules folder.
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets from the builder stage to the correct location
# where the standalone server expects them.
COPY --from=builder /app/apps/web/.next/static ./.next/static

# Expose the port Next.js will run on
EXPOSE 3000

# The command to run the Next.js standalone server
CMD ["node", "server.js"] 