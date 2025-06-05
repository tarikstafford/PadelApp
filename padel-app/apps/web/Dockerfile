# Stage 1: Build dependencies and application code
FROM node:18-alpine AS builder

# Set working directory for the entire monorepo context
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Install Turbo globally (or use npx turbo later)
RUN npm install -g turbo

# Copy ALL monorepo files, including .git directory
COPY . .

# (Optional but good practice) Clean pnpm cache if it was copied
# RUN pnpm store prune

# Prune the monorepo to only include dependencies for the 'web' app
RUN turbo prune web --docker

# Stage 2: Install dependencies for the pruned 'web' app
FROM node:18-alpine AS installer

WORKDIR /app

# Install pnpm globally (needed again in this new stage)
RUN npm install -g pnpm

# Copy the pruned monorepo structure (package.json files and lockfile)
COPY --from=builder /app/out/json/ ./ 
COPY --from=builder /app/out/pnpm-lock.yaml ./pnpm-lock.yaml

# Install dependencies using pnpm (only for the 'web' app and its direct dependencies)
RUN pnpm install --frozen-lockfile --prod=false # Install devDependencies if build scripts need them

# Stage 3: Build the Next.js application
FROM node:18-alpine AS runner

WORKDIR /app

# No global turbo install here, we'll rely on npx or project's node_modules

# Copy dependencies from the installer stage
COPY --from=installer /app/node_modules ./node_modules/
COPY --from=installer /app/package.json ./package.json 

# Copy the pruned source code for the 'web' app and its dependencies
COPY --from=builder /app/out/full/ ./

# Debug: List contents of node_modules/.bin to see if turbo is present
RUN ls -la ./node_modules/.bin/

# Attempt to run the build using npx, with verbose flag for Next.js build
RUN npx turbo run build --filter=web -- --verbose

# Stage 4: Production Image - copy only necessary artifacts
FROM node:18-alpine AS production-runner

WORKDIR /app

ENV NODE_ENV production
# ENV NEXT_TELEMETRY_DISABLED 1 # Uncomment to disable Next.js telemetry

# Correctly copy standalone output to the root of /app for production runner
COPY --from=runner /app/apps/web/.next/standalone ./ 
# Static assets are relative to the server.js inside standalone
COPY --from=runner /app/apps/web/.next/static ./apps/web/.next/static 
COPY --from=runner /app/apps/web/public ./apps/web/public

# Set the correct user for running the application (optional but good practice)
# RUN addgroup --system --gid 1001 nodejs
# RUN adduser --system --uid 1001 nextjs
# USER nextjs

EXPOSE 3000

# CMD for standalone output is typically node server.js from the root of the standalone dir
CMD ["node", "server.js"] 