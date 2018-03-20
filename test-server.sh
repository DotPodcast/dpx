#!/bin/sh

echo "Building Docker image"
docker build -t dpx_server_test server > null
BUILD_SUCCESSFUL=$?

if [ $BUILD_SUCCESSFUL -eq 0 ]; then
    echo "Running tests"
    docker run dpx_server_test bash -c "DJANGO_ENVIRONMENT=test python manage.py test"
fi
