# Testing Pawn
from Core.pieces import Pawn
from Core.board import Board

def test_pawn_starting_moves():
    # white pawn starting position
    white = Pawn("white")
    board = Board()
    board.set_piece(6, 0, white)
    moves = white.get_valid_moves(board, 6, 0)
    assert (5, 0) in moves
    assert (4, 0) in moves

    # black pawn starting position
    black = Pawn("black")
    board.set_piece(1, 0, black)
    moves = black.get_valid_moves(board, 1, 0)
    assert (2, 0) in moves
    assert (3, 0) in moves