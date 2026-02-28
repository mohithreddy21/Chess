class Piece:
    def __init__(self,color):
        if not isinstance(color,str):
            raise TypeError("color must be a string")
        normalizedColor = color.lower()
        if normalizedColor in {'white','black'}:
            self.color = normalizedColor
        else:
            raise ValueError("color must be 'white' or 'black', got '{color}'")
        
    def get_valid_moves(self,board,row,col):
        raise NotImplementedError("")
    
    def _slide_moves(self,board,row,col,directions):
        pseudoValidPositions = []
        for delta in directions:
            currentRow, currentCol = (row + delta[0], col + delta[1])
            while board._is_within_bounds(currentRow,currentCol):
                existingPiece = board.get_piece(currentRow,currentCol)
                if existingPiece is None:
                    pseudoValidPositions.append((currentRow,currentCol))
                elif existingPiece.color == self.color:
                    break
                else:
                    pseudoValidPositions.append((currentRow,currentCol))
                    break
                currentRow, currentCol = currentRow + delta[0], currentCol + delta[1]
        return pseudoValidPositions
    

class Rook(Piece):
    DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)] # Up, Down, Left, Right
    def get_valid_moves(self, board, row, col):
        return self._slide_moves(board,row,col,self.DIRECTIONS)
    
class Bishop(Piece):
    DIRECTIONS = [(-1,-1),(1,1),(-1,1),(1,-1)]
    def get_valid_moves(self, board, row, col):
        return self._slide_moves(board,row,col,self.DIRECTIONS)

class Queen(Piece):
    rookDirections = [(-1,0),(1,0),(0,-1),(0,1)]
    bishopDirections = [(-1,-1),(1,1),(-1,1),(1,-1)]
    DIRECTIONS = rookDirections + bishopDirections
    def get_valid_moves(self, board, row, col):
        return self._slide_moves(board,row,col,self.DIRECTIONS)

class Knight(Piece):
    DIRECTIONS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1),  (2, 1), (1, -2),  (1, 2)]

    def get_valid_moves(self, board, row, col):
        pseudoValidPositions = []
        for delta in self.DIRECTIONS:
            currentRow, currentCol = row + delta[0], col + delta[1]
            if board._is_within_bounds(currentRow, currentCol):
                existingPiece = board.get_piece(currentRow, currentCol)
                if existingPiece is None or existingPiece.color != self.color:
                    pseudoValidPositions.append((currentRow, currentCol))
        return pseudoValidPositions
    
class Pawn(Piece):
    def get_valid_moves(self, board, row, col):
        pseudoValidPositions = []
        FORWARD = -1 if self.color == 'white' else 1
        START_ROW = 6 if self.color == 'white' else 1

        if board._is_within_bounds(row + FORWARD, col) and board.get_piece(row + FORWARD, col) is None:
            pseudoValidPositions.append((row + FORWARD, col))

            if row == START_ROW:
                if board._is_within_bounds(row + 2 * FORWARD, col) and board.get_piece(row + 2 * FORWARD, col) is None:
                    pseudoValidPositions.append((row + 2 * FORWARD, col))

        # Diagonal Capture
        diagonals = [(row + FORWARD, col + 1), (row + FORWARD, col - 1)]
        for diagonal in diagonals:
            diagonalRow = diagonal[0]
            diagonalCol = diagonal[1]
            if board._is_within_bounds(diagonalRow, diagonalCol):
                existingPiece = board.get_piece(diagonalRow, diagonalCol)
                if existingPiece is not None and existingPiece.color != self.color:
                    pseudoValidPositions.append((diagonalRow, diagonalCol))

        return pseudoValidPositions

class King(Piece):
    DIRECTIONS = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    
    def get_valid_moves(self, board, row, col):
        pseudoValidPositions = []
        for delta in self.DIRECTIONS:
            currentRow, currentCol = row + delta[0], col + delta[1]
            if board._is_within_bounds(currentRow,currentCol):
                existingPiece = board.get_piece(currentRow,currentCol)
                if existingPiece is None or existingPiece.color != self.color:
                    pseudoValidPositions.append((currentRow,currentCol))
                                
        return pseudoValidPositions


    