# Stage 1: Install dependencies and prepare for pruning
FROM node:18-alpine AS deps_installer
WORKDIR /app

# Install pnpm globally (specific version from your package.json)
RUN npm install -g pnpm@10.4.1

# Copy manifest files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
# If you have a .npmrc at the root, copy it too:
# COPY .npmrc ./ 

# Install all monorepo dependencies. This allows turbo to correctly build the graph.
RUN pnpm install --frozen-lockfile --prod=false # Ensure devDependencies like 'turbo' are available

# Stage 2: Prune and build the specific application ('web')
FROM node:18-alpine AS builder
WORKDIR /app

# Install pnpm and turbo globally for the prune and build commands
RUN npm install -g pnpm@10.4.1 turbo

# Copy manifest files again (needed for turbo prune context)
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
# COPY .npmrc ./

# Copy the fully installed node_modules from the previous stage.
COPY --from=deps_installer /app/node_modules ./node_modules/

# Copy all source code (respecting .dockerignore at the monorepo root)
COPY . .

# Now prune. With all files and node_modules present, prune should understand the graph.
RUN turbo prune web --docker

# Stage 3: Install dependencies for the PRUNED 'web' app
FROM node:18-alpine AS installer
WORKDIR /app
RUN npm install -g pnpm@10.4.1
COPY --from=builder /app/out/json/ ./ 
COPY --from=builder /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
RUN pnpm install --frozen-lockfile --prod=false

# Stage 4: Build the Next.js application (runner)
FROM node:18-alpine AS runner
WORKDIR /app
RUN npm install -g pnpm@10.4.1 turbo
ENV PATH /usr/local/lib/node_modules/.bin:/usr/local/bin:$PATH

COPY --from=builder /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=installer /app/node_modules ./node_modules/
COPY --from=installer /app/package.json ./package.json 
COPY --from=builder /app/out/full/ ./

RUN echo "--- RUNNER STAGE DEBUG ---" && \
    echo "Current PATH: $PATH" && \
    echo "Contents of /app:" && ls -la /app && \
    echo "pnpm version:" && pnpm --version && \
    echo "turbo version:" && turbo --version && \
    echo "--- END RUNNER STAGE DEBUG ---"

RUN turbo run build --filter=web -- --verbose

# Stage 5: Production Image
FROM node:18-alpine AS production-runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=runner /app/apps/web/.next/standalone ./ 
COPY --from=runner /app/apps/web/.next/static ./apps/web/.next/static 
COPY --from=runner /app/apps/web/public ./apps/web/public
EXPOSE 3000
CMD ["node", "server.js"] 