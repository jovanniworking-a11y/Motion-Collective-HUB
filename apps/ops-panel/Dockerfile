# Optional: run the Next ops panel in Docker (Fly / Railway Node).
# Preferred free path for the panel is Vercel (no container needed).
# Build from repo root:
#   docker build -f apps/ops-panel/Dockerfile -t motion-ops-panel .

FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY apps/ops-panel/package.json apps/ops-panel/package-lock.json ./
RUN npm ci

FROM node:22-bookworm-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY apps/ops-panel/ ./
# Bake public API URL at build time (Next inlines NEXT_PUBLIC_*).
ARG NEXT_PUBLIC_API_URL=http://127.0.0.1:8787
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    DOCKER_BUILD=1 \
    NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["sh", "-c", "node server.js"]
