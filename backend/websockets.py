import websockets
import asyncio
import json
from backend.handlers import handle_create, handle_join, handle_move


rooms = {}

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        messageType = data.get('type')
        if messageType == 'create':# { type : '', message: '' }                 
            await handle_create(websocket, rooms)
        elif messageType == 'join':# { type : '', roomId : '', message: '' }
            roomId = data.get('roomId')
            await handle_join(websocket, roomId, rooms) 
        elif messageType == 'move':
            roomId = data.get('roomId')
            move = data.get('move')
            await handle_move(roomId, rooms, move)











async def main():
    async with websockets.serve(handler, 'localhost', 8000) as server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())


















