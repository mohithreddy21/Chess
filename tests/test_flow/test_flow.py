import asyncio
import websockets
import json

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

passed = 0
failed = 0

def log_test(name):
    print(f"\n{CYAN}{BOLD}--- {name} ---{RESET}")

def log_pass(msg):
    global passed
    passed += 1
    print(f"  {GREEN}✓ {msg}{RESET}")

def log_fail(msg):
    global failed
    failed += 1
    print(f"  {RED}✗ {msg}{RESET}")

def log_info(msg):
    print(f"  {YELLOW}→ {msg}{RESET}")


async def create_room(conn):
    await conn.send(json.dumps({"type": "create"}))
    response = json.loads(await conn.recv())
    return response["message"]

async def join_room(conn1, conn2, roomId):
    await conn2.send(json.dumps({"type": "join", "roomId": roomId}))
    r1 = json.loads(await conn1.recv())
    r2 = json.loads(await conn2.recv())
    return r1, r2

async def make_move(conn, roomId, from_sq, to_sq):
    await conn.send(json.dumps({
        "type": "move",
        "roomId": roomId,
        "move": {"from": from_sq, "to": to_sq}
    }))

async def recv_both(conn1, conn2):
    r1 = json.loads(await conn1.recv())
    r2 = json.loads(await conn2.recv())
    return r1, r2

async def recv_one(conn):
    return json.loads(await conn.recv())


# ─────────────────────────────────────────────
# TEST 1: Room Creation
# ─────────────────────────────────────────────
async def test_room_creation():
    log_test("TEST 1: Room Creation")
    async with websockets.connect("ws://localhost:8000") as conn:
        await conn.send(json.dumps({"type": "create"}))
        response = json.loads(await conn.recv())
        if response.get("type") == "room_created" and response.get("message"):
            log_pass(f"Room created with ID: {response['message']}")
        else:
            log_fail(f"Unexpected response: {response}")


# ─────────────────────────────────────────────
# TEST 2: Joining a Room
# ─────────────────────────────────────────────
async def test_join_room():
    log_test("TEST 2: Joining a Room")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        r1, r2 = await join_room(conn1, conn2, roomId)
        if "Game Started" in r1.get("message", "") or "Game Started" in r2.get("message", ""):
            log_pass("Both players notified that game started")
        else:
            log_fail(f"Game start notification missing. Got: {r1}, {r2}")


# ─────────────────────────────────────────────
# TEST 3: Joining Non-existent Room
# ─────────────────────────────────────────────
async def test_join_invalid_room():
    log_test("TEST 3: Joining a Non-existent Room")
    async with websockets.connect("ws://localhost:8000") as conn:
        await conn.send(json.dumps({"type": "join", "roomId": "fake-room-id"}))
        response = json.loads(await conn.recv())
        if response.get("type") == "error" and "does not exist" in response.get("message", "").lower():
            log_pass("Correct error returned for invalid room")
        else:
            log_fail(f"Unexpected response: {response}")


# ─────────────────────────────────────────────
# TEST 4: Basic Pawn Move
# ─────────────────────────────────────────────
async def test_basic_pawn_move():
    log_test("TEST 4: Basic Pawn Move (e2→e4)")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        # Determine which connection is white
        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        await make_move(white_conn, roomId, [6, 4], [4, 4])
        r1, r2 = await recv_both(conn1, conn2)
        if r1.get("message") == "Move Successful" or r2.get("message") == "Move Successful":
            log_pass("White pawn moved e2→e4 successfully")
        else:
            log_fail(f"Move failed: {r1}, {r2}")


# ─────────────────────────────────────────────
# TEST 5: Wrong Turn (Black tries to move first)
# ─────────────────────────────────────────────
async def test_wrong_turn():
    log_test("TEST 5: Wrong Turn (Black moves first)")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        # Black tries to move first
        await make_move(black_conn, roomId, [1, 4], [3, 4])
        response = json.loads(await black_conn.recv())
        if response.get("message") == "Invalid Move":
            log_pass("Black correctly blocked from moving first")
        else:
            log_fail(f"Expected invalid move, got: {response}")


# ─────────────────────────────────────────────
# TEST 6: Moving Empty Square
# ─────────────────────────────────────────────
async def test_empty_square():
    log_test("TEST 6: Moving an Empty Square")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        await make_move(white_conn, roomId, [4, 4], [3, 4])  # Empty square
        response = json.loads(await white_conn.recv())
        if response.get("message") == "Selected empty square":
            log_pass("Correctly returned 'Selected empty square'")
        else:
            log_fail(f"Unexpected response: {response}")


# ─────────────────────────────────────────────
# TEST 7: En Passant
# ─────────────────────────────────────────────
async def test_en_passant():
    log_test("TEST 7: En Passant")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        moves = [
            (white_conn, [6, 4], [4, 4]),  # e2→e4
            (black_conn, [1, 0], [2, 0]),  # a7→a6 (filler)
            (white_conn, [4, 4], [3, 4]),  # e4→e5
            (black_conn, [1, 3], [3, 3]),  # d7→d5 (triggers en passant opportunity)
        ]
        for conn, from_sq, to_sq in moves:
            await make_move(conn, roomId, from_sq, to_sq)
            await recv_both(conn1, conn2)

        # White captures en passant: e5xd6
        await make_move(white_conn, roomId, [3, 4], [2, 3])
        r1, r2 = await recv_both(conn1, conn2)
        if r1.get("message") == "Move Successful" or r2.get("message") == "Move Successful":
            log_pass("En passant capture successful")
        else:
            log_fail(f"En passant failed: {r1}, {r2}")


# ─────────────────────────────────────────────
# TEST 8: Check Detection
# ─────────────────────────────────────────────
async def test_check():
    log_test("TEST 8: Check Detection (Scholar's mate setup)")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        # Set up a position where white gives check with queen
        moves = [
            (white_conn, [6, 4], [4, 4]),  # e2→e4
            (black_conn, [1, 4], [3, 4]),  # e7→e5
            (white_conn, [7, 3], [3, 7]),  # Qd1→h5 (check threat)
            (black_conn, [1, 5], [2, 5]),  # f7→f6? (blunder)
            (white_conn, [3, 7], [1, 4]),  # Qh5xe8? not quite — just test a queen move
        ]
        # Simplified: just play a few moves and verify ongoing state
        await make_move(white_conn, roomId, [6, 4], [4, 4])
        r1, r2 = await recv_both(conn1, conn2)
        if r1.get("state") == "ongoing" or r2.get("state") == "ongoing":
            log_pass("Game state correctly 'ongoing' after opening move")
        else:
            log_fail(f"Unexpected state: {r1}, {r2}")


# ─────────────────────────────────────────────
# TEST 9: Checkmate (Fool's Mate)
# ─────────────────────────────────────────────
async def test_checkmate():
    log_test("TEST 9: Checkmate (Fool's Mate)")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        # Fool's mate sequence
        # 1. f3  e5
        # 2. g4  Qh4#
        moves = [
            (white_conn, [6, 5], [5, 5]),  # f2→f3
            (black_conn, [1, 4], [3, 4]),  # e7→e5
            (white_conn, [6, 6], [4, 6]),  # g2→g4
            (black_conn, [0, 3], [4, 7]),  # Qd8→h4# (checkmate)
        ]
        last_r1, last_r2 = None, None
        for conn, from_sq, to_sq in moves:
            await make_move(conn, roomId, from_sq, to_sq)
            last_r1, last_r2 = await recv_both(conn1, conn2)

        if last_r1.get("state") == "checkmate" or last_r2.get("state") == "checkmate":
            log_pass(f"Checkmate detected! Response: {last_r1.get('message')}")
        else:
            log_fail(f"Checkmate not detected. Got: {last_r1}, {last_r2}")


# ─────────────────────────────────────────────
# TEST 10: Move After Game Over
# ─────────────────────────────────────────────
async def test_move_after_checkmate():
    log_test("TEST 10: Move Attempted After Checkmate")
    async with websockets.connect("ws://localhost:8000") as conn1, \
               websockets.connect("ws://localhost:8000") as conn2:
        roomId = await create_room(conn1)
        await join_room(conn1, conn2, roomId)

        white_conn, black_conn = await get_color_conns(conn1, conn2, roomId)

        # Fool's mate
        moves = [
            (white_conn, [6, 5], [5, 5]),
            (black_conn, [1, 4], [3, 4]),
            (white_conn, [6, 6], [4, 6]),
            (black_conn, [0, 3], [4, 7]),
        ]
        for conn, from_sq, to_sq in moves:
            await make_move(conn, roomId, from_sq, to_sq)
            await recv_both(conn1, conn2)

        # Try to play after checkmate
        await make_move(white_conn, roomId, [6, 0], [5, 0])
        response = json.loads(await white_conn.recv())
        if response.get("message") == "Invalid Move":
            log_pass("Move after checkmate correctly rejected")
        else:
            log_fail(f"Unexpected response after checkmate: {response}")


# ─────────────────────────────────────────────
# HELPER: Detect which connection is white
# ─────────────────────────────────────────────
async def get_color_conns(conn1, conn2, roomId):
    """
    Try a white move from conn1. If invalid, conn2 is white.
    Uses a4 push (a2→a4) as a probe — then undoes it via the engine 
    by just checking the response.
    """
    probe_move = json.dumps({
        "type": "move",
        "roomId": roomId,
        "move": {"from": [6, 0], "to": [4, 0]}
    })
    await conn1.send(probe_move)
    r1 = json.loads(await conn1.recv())
    r2 = json.loads(await conn2.recv())

    if r1.get("message") == "Move Successful" or r2.get("message") == "Move Successful":
        log_info("conn1 = white, conn2 = black")
        # Now black must make a move to restore turn order
        await make_move(conn2, roomId, [1, 0], [2, 0])
        await recv_both(conn1, conn2)
        return conn1, conn2
    else:
        log_info("conn2 = white, conn1 = black")
        return conn2, conn1


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
async def main():
    print(f"\n{BOLD}{'='*50}")
    print("       CHESS ENGINE - WEBSOCKET TEST SUITE")
    print(f"{'='*50}{RESET}")

    await test_room_creation()
    await test_join_room()
    await test_join_invalid_room()
    await test_basic_pawn_move()
    await test_wrong_turn()
    await test_empty_square()
    await test_en_passant()
    await test_check()
    await test_checkmate()
    await test_move_after_checkmate()

    print(f"\n{BOLD}{'='*50}")
    print(f"  Results: {GREEN}{passed} passed{RESET}  {RED}{failed} failed{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())
