import json
from fastapi import WebSocket, WebSocketDisconnect
from server.utils.jwt import verify_access_token
from server.db.core import insert_message, mark_messages_as_read_upto

websocket_clients: dict[int, WebSocket] = {}


async def websocket_endpoint(websocket: WebSocket):
    token: str = websocket.query_params.get("token")
    payload: dict | None = verify_access_token(token) if token else None

    if not payload:
        print("⚠️ WebSocket rejected: invalid token")
        await websocket.close(1008, "Invalid token")
        return

    user_id: int = payload["user_id"]

    if user_id in websocket_clients:
        print(f"⚠️ User {user_id} already connected, closing new connection")
        await websocket.close(1008, "User already connected")
        return

    websocket_clients[user_id] = websocket
    await websocket.accept()
    print(f"✅ User {user_id} connected")

    try:
        while True:
            try:
                data: dict = await websocket.receive_json()
                print(f"📩 User {user_id} sent: {data}")

                payload: dict | None = verify_access_token(data.get("token"))
                if not payload:
                    print(f"⚠️ User {user_id} sent invalid token")
                    await websocket.close(1008, "Invalid token")
                    websocket_clients.pop(user_id, None)
                    return

                if data["type"] == "send_message":
                    receiver_id: int = data["receiver_id"]
                    message: str = data["message"]

                    message_id, timestamp, username, display_name = await insert_message(
                        user_id, receiver_id, message
                    )

                    message_ack_data: dict = {
                        "type": "message_ack",
                        "sender_id": receiver_id,
                        "temp_id": data["temp_id"],
                        "timestamp": timestamp.isoformat(),
                        "message_id": message_id,
                    }
                    await websocket.send_json(message_ack_data)
                    print(f"📤 Ack sent to {user_id}: {message_ack_data}")

                    new_message_data: dict = {
                        "type": "new_message",
                        "message_id": message_id,
                        "sender_id": user_id,  # Доделать кашу
                        "display_name": display_name,
                        "username": username,
                        "message": message,
                        "timestamp": timestamp.isoformat(),
                        "status": "received",
                    }
                    if receiver_id in websocket_clients:
                        await websocket_clients[receiver_id].send_json(new_message_data)
                        print(f"✅ Delivered message {message_id} from {user_id} to {receiver_id}")

                elif data["type"] == "read_messages":
                    message_id: int = data["message_id"]
                    receiver_id = data["receiver_id"]

                    await mark_messages_as_read_upto(message_id, sender_id=receiver_id, receiver_id=user_id)

                    read_message_data: dict = {
                        "type": "messages_read",
                        "reader_id": user_id,
                        "message_id": message_id,
                    }
                    if receiver_id in websocket_clients:
                        await websocket_clients[receiver_id].send_json(read_message_data)
                        print(f"👁 User {user_id} marked messages as read up to {message_id} for {receiver_id}")

            except (json.JSONDecodeError, KeyError):
                print(f"❌ User {user_id} sent invalid JSON: {data}")
                await websocket.send_json({"type": "error", "msg": "Invalid json data"})

    except WebSocketDisconnect:
        websocket_clients.pop(user_id, None)
        print(f"❎ User {user_id} disconnected")