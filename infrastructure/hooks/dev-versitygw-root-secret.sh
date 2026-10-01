#!/usr/bin/env bash
# Development only: create the versitygw namespace and the root S3 credentials
# secret for versitygw. Idempotent; an existing secret is never rotated.
set -euo pipefail

kubectl create namespace versitygw --dry-run=client --output yaml | kubectl apply --filename -

if kubectl --namespace versitygw get secret versitygw-root-secret >/dev/null 2>&1; then
  exit 0
fi

access_key=$(head -c 32 /dev/urandom | base64 | tr -d '=+/\n')
secret_key=$(head -c 32 /dev/urandom | base64 | tr -d '=+/\n')
kubectl --namespace versitygw create secret generic versitygw-root-secret \
  --from-literal rootAccessKeyId="$access_key" \
  --from-literal rootSecretAccessKey="$secret_key" \
  --dry-run=client --output yaml | kubectl apply --filename -
