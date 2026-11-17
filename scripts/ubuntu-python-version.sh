#!/usr/bin/env bash
set -euo pipefail

out_dir=$(mktemp -d)
trap 'rm -rf "$out_dir"' EXIT

docker build --pull --quiet --output "type=local,dest=$out_dir" - <<'EOF' >/dev/null
FROM ubuntu:26.04 AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && python3 --version > /python-version.txt

FROM scratch
COPY --from=build /python-version.txt /
EOF

cat "$out_dir/python-version.txt"
