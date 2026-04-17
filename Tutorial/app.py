import asyncio
import json
import websockets


rooms = {}

async def handler(websocket):
    roomId = None
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'join':
                roomId = data.get('roomId')
                if rooms.get(roomId):
                    rooms[roomId].append(websocket)
                else:
                    rooms[roomId] = [websocket]
            elif data.get('type') == 'message':
                room = rooms[roomId]
                message = data.get('message')
                recipient = next(ws for ws in room if ws != websocket)
                messageObject = {
                    "type" : "message",
                    "message" : message
                }
                await recipient.send(json.dumps(messageObject))
            elif data.get('type') == 'terminate':
                rooms[roomId].remove(websocket)
    finally:
        if roomId and rooms.get(roomId):
            rooms[roomId].remove(websocket)
        await websocket.close()        



async def main():
    async with websockets.serve(handler, "", 8000) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())