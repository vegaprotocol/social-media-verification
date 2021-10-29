#!/bin/sh

# Go to workspace root directory
WORK_DIR=$(cd -P -- "$(dirname -- "$0")/.." && pwd -P)
cd "${WORK_DIR}"

# disable creation of python bytecode files
export PYTHONDONTWRITEBYTECODE=1

# Get first argument from command line; use test.sh if not set
CMD="${1:-${WORK_DIR}/scripts/test.sh}"

# first/head execution
clear
${CMD}

# wait for file changes and execute command
watchmedo shell-command \
    --patterns="*.py" \
    --recursive \
    --ignore-directories \
    --command="clear && ${CMD}" \
    --drop \
    .
