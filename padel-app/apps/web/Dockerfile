# Stage 1: Build the application
FROM node:18-alpine AS builder
WORKDIR /app
RUN npm install -g pnpm@10.4.1 turbo@2.4.2
COPY . .
RUN pnpm install --frozen-lockfile
RUN turbo run build --filter=web

# Stage 2: Production Image
FROM node:18-alpine AS production-runner

# Set a new working directory for the final application
WORKDIR /app/padelgo-frontend

ENV NODE_ENV production

# Copy the standalone output from the builder stage into the new WORKDIR
COPY --from=builder /app/apps/web/.next/standalone ./

# Copy the static assets to the correct relative location
COPY --from=builder /app/apps/web/.next/static ./.next/static

EXPOSE 3000

# The command to run the Next.js standalone server
CMD ["node", "server.js"] 