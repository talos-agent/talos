# FROST Network Scanner

This is a simple network scanner for discovering FROST nodes on a local network.

## Architecture Overview

The network scanner is a Node.js application that probes a range of IP addresses and ports to find FROST nodes. It uses a multi-port HTTP/HTTPS probing mechanism and UDP multicast discovery for local LAN. The scanner is event-driven and emits `nodeAdded` and `nodeRemoved` events when nodes are discovered or lost.

## Running Locally

To run the network scanner locally, you will need to have Node.js and npm installed.

1.  Clone the repository:
    ```
    git clone https://github.com/your-org/frost-network-scanner
    ```
2.  Install the dependencies:
    ```
    cd frost-network-scanner
    npm install
    ```
3.  Run the scanner:
    ```
    node network-scanner.js
    ```

## Deploying to Prod

The network scanner can be deployed as a Docker container. A `Dockerfile` and a Helm chart are provided in the `charts/frost-network-scanner` directory.

## API Spec (OpenAPI)

An OpenAPI specification for the network scanner's API will be generated in a future step.