# hadolint ignore=DL3018
FROM node:22-alpine AS builder

WORKDIR /build

# Apply alpine security patches
RUN apk update && apk upgrade

COPY package*.json ./
RUN npm ci --only=production

FROM node:22-alpine AS runtime

WORKDIR /app

# Apply alpine security patches
RUN apk update && apk upgrade

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder --chown=appuser:appgroup /build/node_modules ./node_modules

COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
