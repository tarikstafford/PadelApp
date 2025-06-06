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
COPY . .

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Build the specific 'web' application. This command now has access to the ARG.
RUN turbo run build --filter=web

# After build, list the contents of the standalone directory for debugging
RUN ls -R /app/apps/web/.next/standalone

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets from the builder stage
COPY --from=builder /app/apps/web/.next/static ./.next/static

EXPOSE 3000

# The command to run the Next.js standalone server
CMD ["node", "apps/web/server.js"] 