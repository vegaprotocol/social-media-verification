#!/bin/bash -e

# Go to docker directory
WORK_DIR="$(realpath "$(dirname "$0")/../docker")"
cd "${WORK_DIR}"

function on_exit {
  echo "=== Stop docker-compose ==="
  docker-compose down
}

trap on_exit EXIT

# Get first argument from command line; use test.sh if not set
CMD="${1:-./scripts/test-integration.sh}"

echo "=== pre-cleanup ==="
docker-compose down
echo "=== Start docker-compose ==="
docker-compose up -d

echo "=== Run tests ==="
docker-compose exec --workdir "/workspace" workspace "${CMD}"
