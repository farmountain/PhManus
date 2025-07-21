#!/usr/bin/env bash
set -e
IMAGE_TAG=${1:-phmanus:release}
if [ -n "$DOCKER_DRYRUN" ]; then
  echo "docker build -f Dockerfile.release -t \"$IMAGE_TAG\" ."
else
  docker build -f Dockerfile.release -t "$IMAGE_TAG" .
fi
