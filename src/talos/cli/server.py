#!/usr/bin/env python3
from __future__ import annotations

from talos.server.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
