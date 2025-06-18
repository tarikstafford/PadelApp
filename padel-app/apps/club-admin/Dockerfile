# Stage 1: Build the application
FROM node:18-alpine AS builder
WORKDIR /app

# Per Railway docs, declare the ARG in the stage it is required.
ARG NEXT_PUBLIC_API_URL
# Expose the build argument as an environment variable for the build stage.
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Install pnpm
RUN npm install -g pnpm@10.4.1 turbo@2.4.2

# The build context is the monorepo root. COPY . . copies everything.
# The .dockerignore file at the root will prevent copying node_modules, .turbo, .git, etc.
COPY . .

# Install all monorepo dependencies using the lockfile
RUN pnpm install --frozen-lockfile

# Build the specific 'club-admin' application
RUN turbo run build --filter=club-admin

# Stage 2: Production Image
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

# Copy the standalone Next.js server output from the builder stage
# This copies server.js, node_modules, etc. into /app
COPY --from=builder /app/apps/club-admin/.next/standalone ./

# Install ONLY production dependencies using the pruned package.json
RUN pnpm install --prod

# Copy static assets after the install
COPY --from=builder /app/apps/club-admin/.next/static ./.next/static

# Run the Next.js server from the root of the WORKDIR
CMD ["node", "server.js"] 