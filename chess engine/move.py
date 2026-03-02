class Move:
    def __init__(self,fromRow,fromCol,toRow,toCol):
        self.fromRow = fromRow
        self.fromCol = fromCol
        self.toRow = toRow
        self.toCol = toCol
        self.capturedPiece = None

        # To-do: add additional attributes to represent the special cases
        # like en passant, castling, pawn promotion etc.

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.fromRow == other.fromRow and self.fromCol == other.fromCol and self.toRow == other.toRow and self.toCol == other.toCol