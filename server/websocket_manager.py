import json
from fastapi import WebSocket, WebSocketDisconnect
from server.utils.jwt import verify_access_token
from server.db.core import insert_message

websocket_clients: dict[int, WebSocket] = {}


async def websocket_endpoint(websocket: WebSocket):
    token: str = websocket.query_params.get("token")
    payload: dict | None = verify_access_token(token) if token else None

    if not payload:
        await websocket.close(1008, "Invalid token")
        return

    user_id: int = payload["user_id"]
    websocket_clients[user_id] = websocket

    await websocket.accept()

    try:
        while True:
            try:
                data: dict = await websocket.receive_json()

                payload: dict | None = verify_access_token(data["token"])
                if not payload:
                    await websocket.close(1008, "Invalid token")
                    websocket_clients.pop(user_id)
                    return

                if data["type"] == "send_message" and data["message"].strip():
                    receiver_id: int = data["receiver_id"]

                    await insert_message(payload["user_id"], receiver_id, data["message"])
                    if receiver_id in websocket_clients:
                        await websocket_clients[receiver_id].send_json({"type": "new_message",
                                                                        "msg": data["message"]})
            except (json.JSONDecodeError, KeyError):
                await websocket.send_json({"type": "error", "msg": "Invalid json data"})

    except WebSocketDisconnect:
        websocket_clients.pop(user_id)

