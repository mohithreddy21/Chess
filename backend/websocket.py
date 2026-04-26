import websockets
import os
import asyncio
import json
from backend.handlers import handle_create, handle_join, handle_move, handle_disconnect



rooms = {}
websockets_to_roomId = {}

async def handler(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            messageType = data.get('type')
            print(f"Received: {message}")
            if messageType == 'create':# { type : '', message: '' }                 
                await handle_create(websocket, rooms, websockets_to_roomId)
            elif messageType == 'join':# { type : '', roomId : '', message: '' }
                roomId = data.get('roomId')
                await handle_join(websocket, roomId, rooms, websockets_to_roomId) 
            elif messageType == 'move':
                roomId = data.get('roomId')
                move = data.get('move')
                await handle_move(roomId, rooms, move)
    except(websockets.exceptions.ConnectionClosedError):
        roomId = websockets_to_roomId.get(websocket)
        if roomId:
            del websockets_to_roomId[websocket]
            await handle_disconnect(websocket, rooms, roomId)
    finally:
        await websocket.close()







HOST = os.environ.get('HOST', 'localhost')
PORT = os.environ.get('PORT', 8000)


async def main():
    async with websockets.serve(handler, HOST, PORT) as server:
        print("Server started on ws://localhost:8000")
        await server.serve_forever()




















