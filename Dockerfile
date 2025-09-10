FROM python:3.12-slim@sha256:d67a7b66b989ad6b6d6b10d428dcc5e0bfc3e5f88906e67d490c4d3daac57047 AS builder

WORKDIR /app

# Pin versions and timestamps for reproducibility.
ARG SOURCE_DATE_EPOCH=1755248916
ARG DEBIAN_SNAPSHOT=20250815T025533Z
ARG DEBIAN_DIST=trixie
ARG UV_VERSION=0.8.11
# Do not include uv metadata as that includes non-reproducable timestamps.
ARG UV_NO_INSTALLER_METADATA=1
# Disable emitting debug symbols as those can contain randomized local paths.
ARG CFLAGS="-g0"

# Install Debian packages.
RUN rm -f /etc/apt/sources.list.d/* && \
    echo "deb [check-valid-until=no] https://snapshot.debian.org/archive/debian/${DEBIAN_SNAPSHOT} ${DEBIAN_DIST} main" > /etc/apt/sources.list && \
    echo "deb [check-valid-until=no] https://snapshot.debian.org/archive/debian-security/${DEBIAN_SNAPSHOT} ${DEBIAN_DIST}-security main" >> /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/10no-check-valid-until && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev

# Install uv for Python package management.
RUN pip install uv==${UV_VERSION}

# Create virtualenv and install Python dependencies.
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/
# Ensure all source files have fixed timestamps, permissions and owners.
RUN find -exec touch -d @${SOURCE_DATE_EPOCH} "{}" \; && \
    find -type f -exec chmod 644 "{}" \; && \
    find -type d -exec chmod 755 "{}" \; && \
    chown -R root:root .

RUN uv venv && \
    . .venv/bin/activate && \
    uv sync --locked

FROM python:3.12-slim@sha256:d67a7b66b989ad6b6d6b10d428dcc5e0bfc3e5f88906e67d490c4d3daac57047

WORKDIR /app

ARG SOURCE_DATE_EPOCH

# Create data directory
RUN mkdir -p /app/data

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/alembic /app/alembic
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Required environment variables (must be provided at runtime):
# - OPENAI_API_KEY: OpenAI API key for AI functionality
# - GITHUB_API_TOKEN: GitHub token for repository operations
# - TWITTER_BEARER_TOKEN: Twitter API bearer token for social media features
# - PINATA_API_KEY: Pinata API key for IPFS operations
# - PINATA_SECRET_API_KEY: Pinata secret key for IPFS operations

EXPOSE 8080

CMD ["python", "-m", "talos.cli.server"]
