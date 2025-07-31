import json
from fastapi import WebSocket, WebSocketDisconnect
from server.utils.jwt import verify_access_token

websocket_clients: list[WebSocket] = []


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)

    try:
        while True:
            try:
                data: dict = await websocket.receive_json()

                if not verify_access_token(data["token"]):
                    await websocket.close(1008, "Invalid token")
                    websocket_clients.remove(websocket)
                    return

                if data["type"] == "ping":
                    await websocket.send_json({"msg": "pong"})
                else:
                    print(data)

            except (json.JSONDecodeError, KeyError):
                print("error: invalid json data")

    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
