from fastapi import FastAPI
from server.db.core import create_tables
from server.api import auth, users
from server.websocket_manager import websocket_endpoint

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)

app.add_api_websocket_route("/ws", websocket_endpoint)

create_tables()

