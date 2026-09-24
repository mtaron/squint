#!/usr/bin/env bash
# Development only: create the temporal namespace and copy the temporal role's
# password from the postgres namespace. Idempotent.
set -euo pipefail

kubectl create namespace temporal --dry-run=client --output yaml | kubectl apply --filename -

password=$(kubectl --namespace postgres get secret temporal-db-secret --output jsonpath='{.data.password}' | base64 --decode)
kubectl --namespace temporal create secret generic temporal-db-secret \
  --from-literal password="$password" \
  --dry-run=client --output yaml | kubectl apply --filename -
