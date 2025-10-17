# Tier‑0 DeSci Platform

A reproducible research environment for adaptive control experiments, powered by **Parallax** (decentralized inference) and **Lattica** (peer‑to‑peer data transport).

## Table of Contents
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing & CI](#testing--ci)
- [Docker & Database](#docker--database)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourorg/tier0-desci.git
cd tier0-desci

# 2. Set up the Python environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Spin up Postgres
docker compose up -d postgres
docker compose ps   # verify it's up

# 4. Run migrations
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/tier0"
psql $DATABASE_URL -f db/migrations/001_init_trials_table.sql

# 5. Run the test suite
pytest -v tests/
```

> **Tip:** The `DATABASE_URL` can be placed in a `.env` file and loaded automatically by Docker Compose.

---

## Project Structure

```
tier0-desci/
├── src/
│   ├── controllers/
│   │   └── z_adaptive.py
│   ├── plants/
│   │   ├── base.py
│   │   └── inverted_pendulum.py
│   └── metrics/
│       └── performance.py
├── api/
│   └── app.py               # Flask entry‑point
├── db/
│   └── migrations/
├── ui/
│   └── src/                 # Front‑end (React/Vue/etc.)
├── tests/
│   ├── test_z_adaptive.py
│   └── test_integration.py
├── docker-compose.yml
├── requirements.txt
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Development Workflow

```bash
# Create a feature branch
git checkout -b feature/tier-0-core

# Make changes, then:
git add .
git commit -m "feat: implement ZAdaptiveController"

# Push and open a PR
git push -u origin feature/tier-0-core
```

The CI pipeline will automatically run linting, tests, and build the Docker images.

---

## Testing & CI

- **Unit tests** – `pytest tests/ -v`
- **Lint** – `ruff src/ tests/`
- **CI file** – `.github/workflows/ci.yml`

---

## Docker & Database

```yaml
# docker-compose.yml (excerpt)
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tier0
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## Contributing

- Open an issue before starting large changes.
- Follow the **Conventional Commits** format.
- Run `pre-commit run --all-files` before pushing.

---

## License

[MIT License](LICENSE)

---

*Built with 🧩 Parallax, 🌐 Lattica, and the open‑source community.*