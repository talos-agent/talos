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

USER talos

EXPOSE 8000

CMD ["python", "-m", "talos.cli.daemon"]
