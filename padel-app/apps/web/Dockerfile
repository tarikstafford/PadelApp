# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Declare the ARG at the top of the stage
ARG NEXT_PUBLIC_API_URL
# Expose it as an environment variable for the build stage
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Install pnpm and turbo globally
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy manifest and config files first
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY .npmrc ./.npmrc
COPY tsconfig.json ./tsconfig.json
COPY postcss.config.mjs ./postcss.config.mjs

# Copy source code for all apps and packages
COPY apps ./apps
COPY packages ./packages

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

# Copy the static assets and public folder from the builder stage
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public

EXPOSE 3000

# The command to run the Next.js standalone server
CMD ["node", "apps/web/server.js"] 