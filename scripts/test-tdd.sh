#!/bin/sh

# Go to workspace root directory
WORK_DIR=$(cd -P -- "$(dirname -- "$0")/.." && pwd -P)
cd "${WORK_DIR}"

# disable creation of python bytecode files
export PYTHONDONTWRITEBYTECODE=1

# command to run tests
cmd="${WORK_DIR}/scripts/test.sh"

# first/head execution
clear
${cmd}

# wait for file changes and execute command
watchmedo shell-command \
    --patterns="*.py" \
    --recursive \
    --ignore-directories \
    --command="clear && ${cmd}" \
    --drop \
    .
