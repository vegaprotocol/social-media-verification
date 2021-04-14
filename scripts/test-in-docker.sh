#!/bin/bash

# Go to workspace root directory
WORK_DIR="$(realpath "$(dirname "$0")/..")"
cd "${WORK_DIR}"

# Get first argument from command line; use test.sh if not set
CMD="${1:-./scripts/test.sh}"

# build docker image
docker build --file ./scripts/test.dockerfile --tag "smv-test" .

# run command in docker container
docker run -it --rm \
    --volume "$(pwd)":/workspace:ro \
    --workdir /workspace \
    --env PYTHONPATH=./src \
    "smv-test" \
    "${CMD}"


