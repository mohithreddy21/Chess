import asyncio
import json
import uuid
from backend.room import Room, RoomState
from Core.move import Move

# Websocket handlers
async def handle_create(websocket, rooms, websockets_to_roomId):
    roomId = str(uuid.uuid4()) # This creates a random uuid which is room id
    room = Room(roomId)
    room.add_participants(websocket)
    websockets_to_roomId[websocket] = roomId
    rooms[roomId] = room
    
    message = json.dumps({ 'type': 'room_created', 'message' : roomId })
    await websocket.send(message)


async def handle_join(websocket, roomId, rooms, websockets_to_roomId):
    room = rooms.get(roomId)
    message = ''
    if not room:
        message = 'Room does not exist'
        await websocket.send(json.dumps({'type' : 'error', 'message' : message}))
        return
    else:
        message = 'Joined room successfully'
        websockets_to_roomId[websocket] = roomId
        roomFull = room.add_participants(websocket)
        if roomFull:
            participants = room.participants
            for color, player in participants.items():
                message = f"Game Started, Color Assigned {color}"
                await room.notify_players('color_assigned', message, notify = color)
            return
    await room.notify_players('joined', message)
    
async def handle_move(roomId, rooms, moveRecieved):
    fromCoordinates, toCoordinates = moveRecieved['from'], moveRecieved['to']
    move = Move(fromCoordinates[0], fromCoordinates[1], toCoordinates[0], toCoordinates[1])
    room = rooms.get(roomId)
    status, extra, player = room.engine.play_move(move)
    message = ''
    if status == 'checkmate':
        room.state = RoomState.FINISHED
        winner = extra
        message = f"{winner} wins!"
        await room.notify_players('finished', message, status)
    elif status == 'stalemate':
        room.state = RoomState.FINISHED
        message = "Game Ends with a Draw"
        await room.notify_players('finished', message, status)
    elif status == 'ongoing':
        room.state = RoomState.ONGOING
        message = "Move Successful"
        await room.notify_players('move', message)
    elif status == 'invalid':
        room.state = RoomState.ONGOING
        message = 'Invalid Move'
        await room.notify_players('move', message, notify = player)
    elif status == 'empty':
        room.state = RoomState.ONGOING
        message = 'Selected empty square'
        await room.notify_players('move', message, notify = player)


async def handle_disconnect(websocket, rooms, roomId):
    room = rooms[roomId]
    players = room.participants.items()
    playerDisconnected = websocket
    playerOnline = None
    for color, player in players:
        if player != playerDisconnected:
            playerOnline = color
    message = "Player Disconnected"
    room.state = RoomState.FINISHED
    await room.notify_players('error', message, notify = playerOnline)

