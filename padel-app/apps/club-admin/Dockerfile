# Stage 1: Build the application
FROM node:18-alpine AS builder
WORKDIR /app

# Install pnpm and turbo globally
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# Copy the root package.json, pnpm-lock.yaml, and .npmrc
COPY package.json pnpm-lock.yaml .npmrc ./

# Copy the package.json files for all workspaces
COPY apps/api/package.json ./apps/api/
COPY apps/web/package.json ./apps/web/
COPY apps/club-admin/package.json ./apps/club-admin/
COPY packages/ui/package.json ./packages/ui/

# Install all monorepo dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the source code
COPY . .

# Build the specific 'club-admin' application
RUN turbo run build --filter=club-admin

# Stage 2: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
COPY --from=builder /app/apps/club-admin/.next/standalone ./

# Copy the static assets from the builder stage
COPY --from=builder /app/apps/club-admin/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"] 