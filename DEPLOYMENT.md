# ROFL Deployment

The Talos agent is deployed in a TEE via [ROFL] using on-chain governance. In order to propose a
new release for approval and deployment, the following steps should be taken.

[ROFL]: https://docs.oasis.io/build/rofl

## Build and Push Container Images

Build and push the new production Docker images by running:

```bash
./scripts/build_and_push_container_image.sh
```

After the build process completes successfully, you should get output like the following:
```
=> [auth] talos-agent/talos:pull,push token for ghcr.io                                                                                                  0.0s
=> resolving provenance for metadata file                                                                                                                0.0s
ghcr.io/talos-agent/talos:latest-agent@sha256:00a7ed860e2bcf16627a4ecd2d98fae4c7e9936774366829892d18fb959f80b2
```

The last line contains the resulting image reference.

## Update Compose File

Update the ROFL-specific compose file (`docker-compose.rofl.yaml`) to make sure that it references
the correct image by its SHA256 hash as returned by the previous step.

```yaml
services:
  talos-agent:
    build: .
    # NOTE: Run ./scripts/build_and_push_container_image.sh to retrieve the digest.
    image: ghcr.io/talos-agent/talos:latest-agent@sha256:00a7ed860e2bcf16627a4ecd2d98fae4c7e9936774366829892d18fb959f80b2
    container_name: talos-agent
    # ... other parts omitted ...
```

## Rebuild App and Update Manifest

Rebuild the app by running:

```bash
oasis rofl build --deployment mainnet
```

This will update the `rofl.yaml` with the new app identity.

## Create a PR

Create a pull request with the above changes and get it merged.

## Tag a New Release

After the pull request is merged, tag a new release and push it by running:

```bash
VERSION=0.1.0
git fetch origin
git merge --ff-only origin/main
git tag v$VERSION main
git push -u origin v$VERSION
```

After the release is pushed, a GitHub action will automatically verify the manifest changes and
if all checks pass, generate a proposal for on-chain approval.

## Get On-chain Approval

After the proposal is generated it will automatically appear in governance interface for review and
approval. When the quorum of signers approve the proposal, the new release will be deployed.
