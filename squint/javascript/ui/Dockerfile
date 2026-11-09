# syntax=docker/dockerfile:1
# Build from the squint/javascript workspace root

ARG BASE_IMAGE=node:24-trixie-slim

FROM ${BASE_IMAGE} AS base

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    npm_config_store_dir=/pnpm/store

RUN corepack enable && mkdir /app && chown node:node /app

USER node
WORKDIR /app

FROM base AS manifests

# Only the manifests, so source edits don't invalidate the dependency layer
COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY --chown=node:node ui/package.json ui/
COPY --chown=node:node db/package.json db/

FROM manifests AS deps

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile --filter @squint/ui...

# Runs the Vite dev server; Tilt live updates the source in place
FROM deps AS dev

COPY --chown=node:node ui ui
COPY --chown=node:node db db

WORKDIR /app/ui

# For dev tools run with `kubectl exec`, such as the auth CLI
ENV PATH=/app/ui/node_modules/.bin:$PATH

EXPOSE 3000 9229

CMD ["node", "--inspect=0.0.0.0:9229", "node_modules/vite/bin/vite.js", "dev", "--host", "0.0.0.0", "--port", "3000"]

FROM deps AS build

COPY --chown=node:node ui ui
COPY --chown=node:node db db

RUN pnpm --filter @squint/ui build

FROM manifests AS prod-deps

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile --prod --filter @squint/ui

FROM ${BASE_IMAGE}

ENV NODE_ENV=production

USER node
WORKDIR /app/ui

# The workspace keeps the packages in /app/node_modules/.pnpm and links them from ui/node_modules
COPY --from=prod-deps /app/node_modules /app/node_modules
COPY --from=prod-deps /app/ui/node_modules node_modules
COPY --from=build /app/ui/package.json ./
COPY --from=build /app/ui/build build

EXPOSE 3000

CMD ["node", "build"]
