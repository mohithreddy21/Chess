from Core.pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from Core.move import Move
class Board:
    def __init__(self):
        self._grid = [[None for col in range(8)] for row in range(8)]
        self.en_passant_target = None
        self.standard_board()
    
    def standard_board(self):
        for row in [0, 1, 6, 7]:
            color = 'black' if row in [0,1] else 'white'
            for col in range(8):
                if row in [1, 6]:
                    pawn = Pawn(color)
                    self.set_piece(row, col, pawn)
                elif row in [0, 7]:
                    if col in [0, 7]:
                        rook = Rook(color)
                        self.set_piece(row, col, rook)
                    elif col in [1, 6]:
                        knight = Knight(color)
                        self.set_piece(row, col, knight)
                    elif col in [2, 5]:
                        bishop = Bishop(color)
                        self.set_piece(row, col, bishop)
                    elif col == 3:
                        queen = Queen(color)
                        self.set_piece(row, col, queen)
                    elif col == 4:
                        king = King(color)
                        self.set_piece(row, col, king)

                

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
        if move.is_en_passant:
            captured_piece = self.get_piece(move.fromRow, move.toCol)
            self.set_piece(move.fromRow, move.toCol, None)
            move.capturedPiece = captured_piece
        else:
            captured_piece = self.get_piece(move.toRow, move.toCol)
            move.capturedPiece = captured_piece

        self.set_piece(move.fromRow, move.fromCol, None)
        self.set_piece(move.toRow, move.toCol, moving_piece)

    def undo_move(self,move):
        moving_piece = self.get_piece(move.toRow, move.toCol)
        if moving_piece is None:
            raise ValueError("No piece at source square")
        if move.is_en_passant:
            self.set_piece(move.fromRow, move.toCol, move.capturedPiece)
            self.set_piece(move.toRow, move.toCol, None)
        else:
            self.set_piece(move.toRow, move.toCol, move.capturedPiece)
        self.set_piece(move.fromRow, move.fromCol, moving_piece)
        
    