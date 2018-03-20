#!/bin/sh

echo "Building Docker image"
docker build -t dpx_worker_test worker > null
BUILD_SUCCESSFUL=$?

if [ $BUILD_SUCCESSFUL -eq 0 ]; then
    echo "Running tests"
    docker run dpx_worker_test pytest
fi
