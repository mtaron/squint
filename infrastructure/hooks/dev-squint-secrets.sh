#!/usr/bin/env bash
# Development only: create the squint namespace and copy the versitygw root S3
# credentials into it as secret s3, so squint workloads can reach object
# storage. Idempotent; an existing secret is never overwritten.
set -euo pipefail

kubectl create namespace squint --dry-run=client --output yaml | kubectl apply --filename -

if kubectl --namespace squint get secret s3 >/dev/null 2>&1; then
  exit 0
fi

versitygw_secret() {
  kubectl --namespace versitygw get secret versitygw-root-secret --output "jsonpath={.data.$1}" | base64 -d
}

kubectl --namespace squint create secret generic s3 \
  --from-literal AWS_ACCESS_KEY_ID="$(versitygw_secret rootAccessKeyId)" \
  --from-literal AWS_SECRET_ACCESS_KEY="$(versitygw_secret rootSecretAccessKey)" \
  --dry-run=client --output yaml | kubectl apply --filename -
