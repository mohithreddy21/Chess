from Core.pieces import Pawn, Knight, Bishop, Queen, Rook, King
from Core.move import Move

class Engine:
    def __init__(self,board):
        self.board = board
        self.current_turn = 'white'
    

    def is_square_attacked(self, row, col, by_color): # Color of opponent's piece
        # Pawn attack detection
        pawnRow = -1 if by_color == 'black' else 1
        pawnDirections = [(pawnRow,1),(pawnRow,-1)]
        
        for delta in pawnDirections:
            currentRow, currentCol = row + delta[0], col + delta[1]
            if self.board._is_within_bounds(currentRow, currentCol):
                existingPiece = self.board.get_piece(currentRow, currentCol)
                if isinstance(existingPiece, Pawn) and existingPiece.color == by_color:
                    return True
            
        # Knight attack detection 
        
        for delta in Knight.DIRECTIONS:
            currentRow, currentCol = row + delta[0], col + delta[1]
            if self.board._is_within_bounds(currentRow, currentCol):
                existingPiece = self.board.get_piece(currentRow, currentCol)
                if isinstance(existingPiece, Knight) and existingPiece.color == by_color:
                    return True
            
        # Bishop/Queen attack detection

        for delta in Bishop.DIRECTIONS:
            currentRow, currentCol = row + delta[0], col + delta[1]
            while self.board._is_within_bounds(currentRow, currentCol):
                existingPiece = self.board.get_piece(currentRow, currentCol)
                if existingPiece is not None and existingPiece.color == by_color and (isinstance(existingPiece, Bishop) or isinstance(existingPiece, Queen)):
                    return True
                elif existingPiece is not None:
                    break
                currentRow, currentCol = currentRow + delta[0], currentCol + delta[1]

        # Rook / Queen attack detection

        for delta in Rook.DIRECTIONS:
            currentRow, currentCol = row + delta[0], col + delta[1]
            while self.board._is_within_bounds(currentRow, currentCol):
                existingPiece = self.board.get_piece(currentRow, currentCol)
                if existingPiece is not None and existingPiece.color == by_color and (isinstance(existingPiece, Rook) or isinstance(existingPiece, Queen)):
                    return True
                elif existingPiece is not None:
                    break
                currentRow += delta[0]
                currentCol += delta[1]
        
        # King attack detection
        for delta in King.DIRECTIONS:
            currentRow, currentCol = row + delta[0], col + delta[1]
            if self.board._is_within_bounds(currentRow, currentCol):
                existingPiece = self.board.get_piece(currentRow, currentCol)
                if existingPiece is not None and existingPiece.color == by_color and isinstance(existingPiece, King):
                    return True

        return False
    

    def _find_king(self,color):
        for row in range(len(self.board._grid)):
            for col in range(len(self.board._grid[0])):
                square = self.board.get_piece(row,col)
                if isinstance(square, King) and square.color == color:
                    return row, col

    def is_in_check(self,color): # Color of our piece
        kingRow, kingCol = self._find_king(color)
        opponentColor = 'white' if color == 'black' else 'black'
        return self.is_square_attacked(kingRow, kingCol, opponentColor)
    
    def get_legal_moves_for_piece(self, row, col):
        currentPiece = self.board.get_piece(row, col)
        if currentPiece is None:
            return []
        pseudoLegalMoves = currentPiece.get_valid_moves(self.board,row,col)
        LegalMoves = []
        for pMove in pseudoLegalMoves:
            toRow, toCol = pMove
            move = Move(row, col, toRow, toCol)
            if self.board.en_passant_target and (toRow, toCol) == self.board.en_passant_target:
                move.is_en_passant = True
            self.board.make_move(move)
            if not self.is_in_check(currentPiece.color):
                LegalMoves.append(move)
            self.board.undo_move(move)

        return LegalMoves
    
    def switch_turn(self):
        self.current_turn = 'white' if self.current_turn == 'black' else 'black'

    def get_game_state(self):
        for row in range(len(self.board._grid)):
            for col in range(len(self.board._grid[0])):
                currentPiece = self.board.get_piece(row, col)
                if currentPiece is not None and currentPiece.color == self.current_turn:
                    legalMoves = self.get_legal_moves_for_piece(row, col)
                    if len(legalMoves) > 0:
                        return 'ongoing'
        if self.is_in_check(self.current_turn):
            return 'checkmate'
        else:
            return 'stalemate'
    
    def play_move(self, move): # This method simulates a player's turn
        sourcePiece = self.board.get_piece(move.fromRow, move.fromCol)
        if sourcePiece is None:
            return ('empty', None, self.current_turn)
        if sourcePiece.color != self.current_turn:
            return ('invalid', None, self.current_turn)
        legalMoves = self.get_legal_moves_for_piece(move.fromRow, move.fromCol) 
        if move not in legalMoves:
            return ('invalid', None, self.current_turn)
        else:
            self.board.make_move(move)
            if isinstance(sourcePiece, Pawn) and abs(move.toRow - move.fromRow) > 1:
                middleSquare = ((move.fromRow + move.toRow)//2, move.toCol)
                self.board.en_passant_target = middleSquare
            else:
                self.board.en_passant_target = None

            gameState = self.get_game_state()
            if gameState == 'checkmate':
                winner = 'black' if self.current_turn == 'white' else 'white'
                return (gameState, winner, self.current_turn)
            elif gameState == 'stalemate':
                return (gameState, 'Draw', self.current_turn)
            else:
                self.switch_turn()
                return (gameState, None, self.current_turn) # (game sate, extra, player)
            
    