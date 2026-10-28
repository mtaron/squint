# syntax=docker/dockerfile:1

ARG BASE_IMAGE=node:24-trixie-slim

FROM ${BASE_IMAGE} AS base

ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    npm_config_store_dir=/pnpm/store

RUN corepack enable && mkdir /app && chown node:node /app

USER node
WORKDIR /app

FROM base AS deps

# Only the manifests, so source edits don't invalidate the dependency layer
COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile

# Runs the Vite dev server; Tilt live updates the source in place
FROM deps AS dev

COPY --chown=node:node . .

EXPOSE 3000 9229

CMD ["node", "--inspect=0.0.0.0:9229", "node_modules/vite/bin/vite.js", "dev", "--host", "0.0.0.0", "--port", "3000"]

FROM deps AS build

COPY --chown=node:node . .

RUN pnpm build

FROM base AS prod-deps

COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store,uid=1000,gid=1000 \
    pnpm install --frozen-lockfile --prod

FROM ${BASE_IMAGE}

ENV NODE_ENV=production

USER node
WORKDIR /app

COPY --from=prod-deps /app/node_modules node_modules
COPY --from=build /app/package.json ./
COPY --from=build /app/build build
COPY --from=build /app/drizzle drizzle
COPY --from=build /app/server.js ./

EXPOSE 3000

CMD ["node", "server.js"]
