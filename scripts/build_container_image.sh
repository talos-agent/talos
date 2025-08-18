#!/bin/bash

BUILDER_NAME=buildkit_23
BUILDER_IMAGE=moby/buildkit:v0.23.2
SOURCE_DATE_EPOCH=1755248916

# Ensure we use the right buildkit for reproducibility.
if ! docker buildx inspect ${BUILDER_NAME} &>/dev/null; then
    docker buildx create --use --driver-opt image=${BUILDER_IMAGE} --name ${BUILDER_NAME}
fi

# Build the container in a reproducible way.
docker buildx build \
	--builder ${BUILDER_NAME} \
	--no-cache \
	--build-arg SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
	--output type=docker,name=$TARGET_IMAGE,rewrite-timestamp=true \
	.

