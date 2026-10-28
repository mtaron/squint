#!/usr/bin/env bash
# Development only: build the migration image and push it to the kind registry.
set -euo pipefail

image="$1"
workspace="$(git rev-parse --show-toplevel)/squint/javascript"

docker build --file "$workspace/db/Dockerfile" --tag "$image" "$workspace"
docker push "$image"
