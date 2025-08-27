#!/bin/bash

set -e

COMPOSE_FILE=$(yq -r '.artifacts.container.compose' rofl.yaml)
TARGET_IMAGE=$(yq -r '.services."talos-agent".image' ${COMPOSE_FILE} | cut -d '@' -f 1)

BUILDER_NAME=buildkit_23
BUILDER_IMAGE=moby/buildkit:v0.23.2
SOURCE_DATE_EPOCH=1755248916

# Ensure we use the right buildkit for reproducibility.
if ! docker buildx inspect ${BUILDER_NAME} &>/dev/null; then
    docker buildx create --use --driver-opt image=${BUILDER_IMAGE} --name ${BUILDER_NAME}
fi

# Build the container in a reproducible way.
METADATA_FILE=$(mktemp)

docker buildx build \
	--builder ${BUILDER_NAME} \
	--no-cache \
	--provenance false \
	--build-arg SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH}" \
	--output type=registry,name=${TARGET_IMAGE},rewrite-timestamp=true \
	--metadata-file "${METADATA_FILE}" \
	.

# Output the image digest.
IMAGE_NAME=$(jq -r '."image.name" + "@" + ."containerimage.digest"' "${METADATA_FILE}")
if [[ -n "${OUTPUT_IMAGE_NAME_PATH}" ]]; then
    echo "${IMAGE_NAME}" > ${OUTPUT_IMAGE_NAME_PATH}
fi
echo "${IMAGE_NAME}"
