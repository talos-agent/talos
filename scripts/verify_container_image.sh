#!/bin/bash

set -e

COMPOSE_FILE=$(yq -r '.artifacts.container.compose' rofl.yaml)
TALOS_AGENT_IMAGE=$(yq -r '.services."talos-agent".image' ${COMPOSE_FILE})

if [[ "${TALOS_AGENT_IMAGE}" != "${EXPECTED_TALOS_AGENT_IMAGE}" ]]; then
  echo "Talos agent image mismatch:"
  echo ""
  echo "  Configured in ${COMPOSE_FILE}:"
  echo "    ${TALOS_AGENT_IMAGE}"
  echo ""
  echo "  Built locally:"
  echo "    ${EXPECTED_TALOS_AGENT_IMAGE}"
  echo ""
  exit 1
fi
