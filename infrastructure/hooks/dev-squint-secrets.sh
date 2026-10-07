#!/usr/bin/env bash
# Development only secret copying across namespaces.
# This would use workload identity in production.
set -euo pipefail

kubectl create namespace squint --dry-run=client --output yaml | kubectl apply --filename -

secret_exists() {
  kubectl --namespace squint get secret "$1" >/dev/null 2>&1
}

# secret_value NAMESPACE SECRET KEY
secret_value() {
  kubectl --namespace "$1" get secret "$2" --output "jsonpath={.data.$3}" | base64 -d
}

if ! secret_exists s3; then
  kubectl --namespace squint create secret generic s3 \
    --from-literal AWS_ACCESS_KEY_ID="$(secret_value versitygw versitygw-root-secret rootAccessKeyId)" \
    --from-literal AWS_SECRET_ACCESS_KEY="$(secret_value versitygw versitygw-root-secret rootSecretAccessKey)" \
    --dry-run=client --output yaml | kubectl apply --filename -
fi

if ! secret_exists postgres; then
  kubectl --namespace squint create secret generic postgres \
    --from-literal PGUSER="$(secret_value postgres postgres-cluster-app username)" \
    --from-literal PGPASSWORD="$(secret_value postgres postgres-cluster-app password)" \
    --from-literal PGDATABASE="$(secret_value postgres postgres-cluster-app dbname)" \
    --dry-run=client --output yaml | kubectl apply --filename -
fi
