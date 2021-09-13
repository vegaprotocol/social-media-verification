#!/bin/bash
echo 123

# Go to workspace root directory
WORK_DIR=$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd "${WORK_DIR}"

# disable creation of python bytecode files
export PYTHONDONTWRITEBYTECODE=1

export PYTHONPATH=".:src/"

# run pytest with coverage
python3 -m pytest -p no:cacheprovider \
                  tests/integration
