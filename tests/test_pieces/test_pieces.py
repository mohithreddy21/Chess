# Testing Pawn
import pytest
from Core.pieces import Pawn
from Core.board import Board


@pytest.mark.parametrize("color, row, col", [("white", 6, 0), ("black", 1, 0)])
def test_pawn_starting_moves(color, row, col):
    # white pawn starting position
    pawn = Pawn(color)
    board = Board()
    board.set_piece(row, col, pawn)
    moves = pawn.get_valid_moves(board, row, col)
    FORWARD = -1 if color == 'white' else 1
    assert (row + FORWARD, 0) in moves
    assert (row + 2 * FORWARD, 0) in moves


@pytest.mark.parametrize("color,row,blocker_row", [
    ("white", 4, 3),
    ("black", 3, 4),
])
def test_pawn_blocked(color, row, blocker_row):
    board = Board()
    pawn = Pawn(color)
    blocker = Pawn("black" if color == "white" else "white")
    board.set_piece(row, 0, pawn)
    board.set_piece(blocker_row, 0, blocker)
    moves = pawn.get_valid_moves(board, row, 0)
    assert len(moves) == 0