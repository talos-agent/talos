# pinn_api_96m.py
import asyncio
import json
from datetime import datetime

import numpy as np
from fastapi import FastAPI, WebSocket

app = FastAPI()


class PlanetaryPinnAPI:
    def __init__(self):
        self.participant_counter = 0

    async def connect_mind(self, websocket: WebSocket, mind_id: str):
        await websocket.accept()
        self.participant_counter += 1
        print(f"🧠 Mente conectada: {mind_id} (Total: {self.participant_counter})")
        try:
            while True:
                data = await websocket.receive_json()
                await websocket.send_json(
                    {
                        "coherence": 0.85,
                        "participants": self.participant_counter,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
        except:
            pass
        finally:
            self.participant_counter -= 1


@app.websocket("/ws/{mind_id}")
async def websocket_endpoint(websocket: WebSocket, mind_id: str):
    api = PlanetaryPinnAPI()
    await api.connect_mind(websocket, mind_id)
