from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState
from db.mongosdb import get_database
from crud.chat import get_room, insert_room, manager, upload_message_to_room
import json
router = APIRouter()

@router.websocket("/chat/{room_name}/{current_username}")
async def websocket_endpoint(db: AsyncIOMotorClient = Depends(get_database), websocket: WebSocket = WebSocket, room_name: str = None, current_username: str = None):
    try:
        await manager.connect(websocket, room_name, current_username)
        await insert_room(db, current_username, room_name)
        room = await get_room(db, room_name)
        data = {
            "content": f"{current_username} has created the chat.",
            "user": current_username,
            "room_name": room_name,
            "type":"entrance",
            "room_object": str(room['_id'])
        }

        await manager.broadcast(data)

        # wait for messages

        while True:
            if websocket.application_state == WebSocketState.CONNECTED:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                if "type" in message_data and message_data["type"] == "dismissal":
                    await manager.disconnect(websocket, room_name)
                    break
                else:
                    await upload_message_to_room(db,data)
                    await manager.broadcast(f"{data}")
            else:
                await manager.connect(websocket, room_name)

    except Exception as e:
        print()
        print("could not connect --> ", e)
        print(type(e).__name__, e.args)
        print()

        manager.disconnect(websocket, current_username)