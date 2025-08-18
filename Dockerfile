FROM python:3.12-slim@sha256:d67a7b66b989ad6b6d6b10d428dcc5e0bfc3e5f88906e67d490c4d3daac57047 AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN python -m pip install --no-cache-dir uv==0.2.22

COPY requirements.txt pyproject.toml README.md ./
COPY src/ ./src/

# Use a filtered requirements file to avoid installing the local package (which would re-resolve deps)
RUN grep -v '^\-e file:///app$' requirements.txt > requirements.lock && \
    uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.lock

FROM python:3.12-slim@sha256:d67a7b66b989ad6b6d6b10d428dcc5e0bfc3e5f88906e67d490c4d3daac57047 AS runtime

WORKDIR /app

RUN useradd --create-home --shell /bin/bash talos

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Required environment variables (must be provided at runtime):
# - OPENAI_API_KEY: OpenAI API key for AI functionality
# - GITHUB_API_TOKEN: GitHub token for repository operations
# - TWITTER_BEARER_TOKEN: Twitter API bearer token for social media features
# - PINATA_API_KEY: Pinata API key for IPFS operations
# - PINATA_SECRET_API_KEY: Pinata secret key for IPFS operations

USER talos

EXPOSE 8000

CMD ["python", "-m", "talos.cli.daemon"]
