# src/talos/tools/twitch_listener.py
import os
import time
from typing import Any

from twitchAPI.chat import Chat, ChatMessage, EventData
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, ChatEvent


class AOMock:
    def send(self, message_payload: dict[str, Any]) -> dict[str, Any]:
        print("[AO.SEND] ✅ Mensagem enviada com sucesso.")
        print(f"[AO.SEND]   Action: {message_payload.get('Action', 'N/A')}")
        print(f"[AO.SEND]   Target: {message_payload.get('Target', 'N/A')}")
        return {"status": "Success", "id": f"tx_{time.time()}"}


ao_mock = AOMock()


async def on_ready(ready_event: EventData, channel_name: str) -> None:
    """Event handler for when the bot is ready."""
    print("Bot is ready for work, joining channels")
    await ready_event.chat.join_room(channel_name)
    print(f"Joined channel: {channel_name}")


async def on_message(msg: ChatMessage) -> None:
    """Event handler for when a message is received."""
    if not msg.text or msg.text.startswith("!"):
        print(f"[EVENTO CHAT] Mensagem vazia ou comando interno ignorado de {msg.user.name}.")
        return

    timestamp = int(time.time())

    payload = {
        "Action": "DATA_EVENT",
        "SourceChannel": f"#{msg.room.name}",
        "EventType": "chat",
        "Timestamp": timestamp,
        "Payload User": msg.user.name,
        "Payload Msg": msg.text,
        "Target": "AO_GAME_PROCESS_ID_SANDBOX",
    }

    ao_mock.send(payload)


async def run(channel_name: str) -> None:
    """Main function to run the Twitch listener."""
    APP_ID = os.environ.get("TWITCH_APP_ID")
    APP_SECRET = os.environ.get("TWITCH_APP_SECRET")
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]

    if not APP_ID or not APP_SECRET:
        raise ValueError("TWITCH_APP_ID and TWITCH_APP_SECRET environment variables must be set.")

    twitch = await Twitch(APP_ID, APP_SECRET)

    # For a non-interactive flow, you would typically use a pre-generated token.
    # For this example, we will stick to the UserAuthenticator for simplicity,
    # but in a real-world scenario, you would manage the token differently.
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(twitch)

    chat.register_event(ChatEvent.READY, lambda ready_event: on_ready(ready_event, channel_name))
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.start()

    print("Twitch listener started. Press Enter to stop.")
    try:
        input()
    finally:
        chat.stop()
        await twitch.close()
