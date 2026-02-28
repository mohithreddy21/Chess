from pieces import Piece
from move import Move
class Board:
    def __init__(self):
        self._grid = [[None for col in range(8)] for row in range(8)]
    
    def _is_within_bounds(self,row,col):
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False
        else:
            return True
    
    def get_piece(self,row,col):
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("This method only accepts integers as coordinates.")
        if self._is_within_bounds(row,col):
            return self._grid[row][col]
        else:
            raise IndexError("Position out of bounds!")
    
    def set_piece(self,row,col,piece):
        if not isinstance(row, int) or not isinstance(col, int):
            raise TypeError("This method only accepts integers as coordinates.")
        if not self._is_within_bounds(row,col):
            raise IndexError("Position out of bounds") 
        if piece is not None and not isinstance(piece, Piece):
            raise TypeError("This method only accepts valid piece")
        else:
            self._grid[row][col] = piece
           
    def make_move(self,move): # move object with all necessary info is passed
        moving_piece = self.get_piece(move.fromRow, move.fromCol)
        if moving_piece is None:
            raise ValueError("No piece at source square")
        captured_piece = self.get_piece(move.toRow, move.toCol)
        self.set_piece(move.fromRow, move.fromCol, None)
        self.set_piece(move.toRow, move.toCol, moving_piece)
        move.capturedPiece = captured_piece

    def undo_move(self,move):
        moving_piece = self.get_piece(move.toRow, move.toCol)
        if moving_piece is None:
            raise ValueError("No piece at source square")
        self.set_piece(move.toRow, move.toCol, move.capturedPiece)
        self.set_piece(move.fromRow, move.fromCol, moving_piece)
        