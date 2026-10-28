# syntax=docker/dockerfile:1
# Applies the Drizzle migrations to $PGDATABASE. Build from the squint/javascript workspace root.

ARG BASE_IMAGE=node:24-trixie-slim

FROM ${BASE_IMAGE} AS deps

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    npm_config_store_dir=/pnpm/store

RUN corepack enable && mkdir /app && chown node:node /app

USER node
WORKDIR /app

COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY --chown=node:node db/package.json db/

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile --prod --filter @squint/db

FROM ${BASE_IMAGE}

USER node
WORKDIR /app/db

COPY --from=deps /app/node_modules /app/node_modules
COPY --from=deps /app/db/node_modules node_modules
COPY --chown=node:node db/package.json db/drizzle.config.ts ./
COPY --chown=node:node db/drizzle drizzle

CMD ["node_modules/.bin/drizzle-kit", "migrate"]
