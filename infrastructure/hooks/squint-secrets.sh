#!/usr/bin/env bash

set -euo pipefail

kubectl create namespace squint --dry-run=client --output yaml | kubectl apply --filename -

secret_value() {
  kubectl --namespace "$1" get secret "$2" --output jsonpath="{.data.$3}" | base64 --decode
}

kubectl --namespace squint create secret generic postgres-app \
  --type kubernetes.io/basic-auth \
  --from-literal username="$(secret_value postgres postgres-cluster-app username)" \
  --from-literal password="$(secret_value postgres postgres-cluster-app password)" \
  --dry-run=client --output yaml | kubectl apply --filename -

kubectl --namespace squint create secret generic s3-credentials \
  --from-literal accessKeyId="$(secret_value versitygw versitygw-root-secret rootAccessKeyId)" \
  --from-literal secretAccessKey="$(secret_value versitygw versitygw-root-secret rootSecretAccessKey)" \
  --dry-run=client --output yaml | kubectl apply --filename -
