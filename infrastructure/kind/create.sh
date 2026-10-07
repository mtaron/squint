#!/usr/bin/env bash
# Based off https://kind.sigs.k8s.io/docs/user/local-registry/ with two major alterations:
#  - nvkind (https://github.com/NVIDIA/nvkind) is used to create the cluster, enabling GPU support
#  - the registry is created with TLS enabled using mkcert
#

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

CLUSTER_NAME="${CLUSTER_NAME:-squint}"

# Start the registry on https://registry.localhost if it isn't already running
if [[ "$(docker inspect --format '{{.State.Running}}' "${REGISTRY_NAME}" 2>/dev/null || true)" != true ]]; then
    docker run --detach --restart=always \
        --publish 127.0.0.1:443:5000 \
        --network bridge \
        --name "${REGISTRY_NAME}" \
        --volume "${CERT_DIR}:/certs:ro" \
        --volume "${REGISTRY_NAME}-data:/var/lib/registry" \
        --env REGISTRY_HTTP_TLS_CERTIFICATE=/certs/dev.pem \
        --env REGISTRY_HTTP_TLS_KEY=/certs/dev-key.pem \
        registry:3
fi

if ! kind get kubeconfig --name "${CLUSTER_NAME}" >/dev/null 2>&1; then
    nvkind cluster create --name "${CLUSTER_NAME}" --config-template cluster.yaml
fi

# Attach the registry to the kind network so the nodes can resolve it by name
if [[ "$(docker inspect --format '{{json .NetworkSettings.Networks.kind}}' "${REGISTRY_NAME}")" == null ]]; then
    docker network connect kind "${REGISTRY_NAME}"
fi

# Advertise the registry to tooling in the cluster
kubectl --context "kind-${CLUSTER_NAME}" apply --filename local-registry-hosting.yaml
