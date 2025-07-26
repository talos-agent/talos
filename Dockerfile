FROM python:3.12-slim as builder

WORKDIR /app

RUN pip install uv

COPY requirements.txt pyproject.toml README.md ./
COPY src/ ./src/

RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt && \
    uv pip install -e .

FROM python:3.12-slim

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
