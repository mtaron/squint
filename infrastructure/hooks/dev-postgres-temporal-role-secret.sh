#!/usr/bin/env bash
# Development only: create the postgres namespace and the credentials secret for
# the postgres "temporal" role. Idempotent; an existing secret is never rotated.
set -euo pipefail

kubectl create namespace postgres --dry-run=client --output yaml | kubectl apply --filename -

if kubectl --namespace postgres get secret temporal-db-secret >/dev/null 2>&1; then
  exit 0
fi

password=$(head -c 32 /dev/urandom | base64 | tr -d '=+/\n')
kubectl --namespace postgres create secret generic temporal-db-secret \
  --type kubernetes.io/basic-auth \
  --from-literal username=temporal \
  --from-literal password="$password" \
  --dry-run=client --output yaml | kubectl apply --filename -
