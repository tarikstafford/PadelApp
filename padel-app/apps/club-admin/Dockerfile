# Stage 1: Build the application
FROM node:18-alpine AS builder
# Set the working directory to the monorepo root
WORKDIR /app

# Per Railway docs, declare the ARG in the stage it is required.
ARG NEXT_PUBLIC_API_URL
# Expose the build argument as an environment variable for the build stage.
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Install pnpm and turbo globally
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy all source code from the build context
COPY ../.. .

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Build the specific 'club-admin' application
RUN turbo run build --filter=club-admin

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
# The source path is now relative to the monorepo root inside the builder
COPY --from=builder /app/apps/club-admin/.next/standalone ./

# Copy the static assets from the builder stage
COPY --from=builder /app/apps/club-admin/.next/static ./.next/static

EXPOSE 3000

# The start command is now just 'node server.js' because we are in the standalone directory
CMD ["node", "server.js"] 