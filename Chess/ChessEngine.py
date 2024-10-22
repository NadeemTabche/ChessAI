"""
This class is responsible for storing all the information about current state of a chess game.
It will also be responsible for determining the valid moves at the current state. It will also keep a move
log.
"""
import pygame as p

p.init()

# Rows start at 0 at the top and 7 at the bottom, while columns start from 0 at the leftmost and 7 at the rightmost
class Gamestate:
    def __init__(self):
        # board is a 8x8 2d list, each element of the list has two characters, the first character represents
        # the colour of piece "b" or "w", the second character represents the type of the piece, "K", "Q", "R",
        # "B", "N" or "P"
        # "--" represents an empty space with no piece

        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves,
                              'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.threeMoveDrawRule = False
        self.fiftyMoveDrawRule = False
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enpassantPossible = ()  # square coordinates where en passant is possible
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.CastleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]
    # takes move as parameter and executes it, this will not work for castling
    # and en passant and pawn promotion
    def makeMove(self, Move):
        self.board[Move.startRow][Move.startCol] = "--"
        self.board[Move.endRow][Move.endCol] = Move.pieceMoved
        self.moveLog.append(Move)  # log the moves so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players

        # update the king's location if moved
        if Move.pieceMoved == 'wK':
            self.whiteKingLocation = (Move.endRow, Move.endCol)
        elif Move.pieceMoved == 'bK':
            self.blackKingLocation = (Move.endRow, Move.endCol)

        # check if move is a pawn promotion
        if Move.isPawnPromotion:
            self.board[Move.endRow][Move.endCol] = Move.pieceMoved[0] + 'Q'  # uses an index at position zero since
            # this is where the colours are stored and concatenates Q to change piece type

        # en passant move
        if Move.isEnpassantMove:
            self.board[Move.startRow][Move.endCol] = '--'  # capturing the pawn

        # update enpassantPossible variable
        if (Move.pieceMoved[1] == 'P') and (
                abs(Move.startRow - Move.endRow) == 2):  # we know start row and endrow are two apart (checks if pawn moved twice)
            self.enpassantPossible = (
                (Move.startRow + Move.endRow) // 2, Move.startCol)  # this will be capture square, column doesnt change
        else:
            self.enpassantPossible = ()  # reset if not en passant not possible

        # castle move
        if Move.isCastleMove:
            if Move.endCol - Move.startCol == 2:  # Kingside castle move
                self.board[Move.endRow][Move.endCol - 1] = self.board[Move.endRow][Move.endCol + 1]  # Moves rook
                self.board[Move.endRow][Move.endCol + 1] = '--'  # erases old rook
            else:  # Queenside Castle
                self.board[Move.endRow][Move.endCol + 1] = self.board[Move.endRow][Move.endCol - 2]  # Moves rook
                self.board[Move.endRow][Move.endCol - 2] = '--'  # erases old rook

        self.enpassantPossibleLog.append(self.enpassantPossible)
        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(Move)
        self.CastleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    # undo the last move
    def undoMove(self):
        if len(self.moveLog) != 0:  # make sure that there is a move to undo
            move = self.moveLog.pop()
            # The initial position of moved piece is set as the piece's position again
            self.board[move.startRow][move.startCol] = move.pieceMoved
            # The final position of the piece (coordinate of capture) is set as the position of the captured piece
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update the king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # Undo Castling Rights
            self.CastleRightsLog.pop()  # get rid of new castle rights from move we are undoing
            self.currentCastlingRights = self.CastleRightsLog[
                -1]  # set the current castle rights to the last one in the list
            # Undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1]  # Moves rook back
                    self.board[move.endRow][move.endCol - 1] = '--'  # erases rook position after undoing move
                else:  # Queenside Castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1]  # Moves rook back
                    self.board[move.endRow][move.endCol + 1] = '--'  # erases old rook position after undoing

            self.checkMate = False
            self.staleMate = False
            self.fiftyMoveDrawRule = False
            self.threeMoveDrawRule = False

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move
        """
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wqs = False
            self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bqs = False
            self.currentCastlingRights.bks = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False

        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    # moves with checks in mind
    def getValidMoves(self):
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs,
                                        self.currentCastlingRights.bqs)  # copy current castling rights
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # squares that piece can move to

                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + (check[2] * i),
                                       kingCol + (check[3] * i))  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[
                            1] == checkCol:  # once you get to piece and checks
                            break
                # get rid of any moves that do not block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            if moves[i].isEnpassantMove:
                                capturedCol = moves[i].endCol
                                capturedRow = moves[i].endRow + 1 if self.whiteToMove else moves[i].endRow - 1
                                if not (capturedRow, capturedCol) in validSquares:
                                    moves.remove(moves[i])
                            else:
                                moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)

        else:  # not in check so all moves are fine
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True


            else:
                self.staleMate = True

        else:
            self.checkMate = False
            self.staleMate = False

        # Fifty Move Draw rule
        FiftyMoveDraw = 0
        for Move in self.moveLog:  # check all moves
            if (Move.pieceMoved[1] != 'P') and Move.pieceCaptured == "--":  # check if move adds to draw counter
                FiftyMoveDraw += 1
            else:
                FiftyMoveDraw = 0  # reset draw counter (draw conducive moves have to be consecutive)
            if FiftyMoveDraw >= 50:  # check if draw counter has exceeded 50 moves
                self.fiftyMoveDrawRule = True  # set stalemate

        # 3 repeated move rule
        threeMoveDrawCounterWhite = 0
        threeMoveDrawCounterBlack = 0
        if len(self.moveLog) >= 5:
            for i in range(0, len(self.moveLog) - 5, 2):
                if self.moveLog[i] == self.moveLog[i + 4]:
                    threeMoveDrawCounterWhite += 1
                else:
                    threeMoveDrawCounterWhite = 0
                if self.moveLog[i + 1] == self.moveLog[i + 5]:
                    threeMoveDrawCounterBlack += 1
                else:
                    threeMoveDrawCounterBlack = 0
            if threeMoveDrawCounterWhite >= 3 and threeMoveDrawCounterBlack >= 3:
                self.threeMoveDrawRule = True
        self.currentCastlingRights = tempCastleRights
        return moves

    # determines if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # determines if enemy can attack the square (r,c)
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch turns
        # generate all opponent's possible moves
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for Move in opponentMoves:
            if Move.endRow == r and Move.endCol == c:  # square is under attack
                return True
        return False

    # moves without checks in mind
    def getAllPossibleMoves(self):
        moves = []  # empty list to add moves to, used as parameters in other subroutines
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in a given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # calls function based on piece type
        return moves

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
            # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + (d[0] * i)
                endCol = startCol + (d[1] * i)
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():  # list allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        enemyType = endPiece[1]
                        # 5 possibilities here in this complex conditional:
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king (this is necessary to
                        # prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and enemyType == 'R') or (4 <= j <= 7 and enemyType == 'B') or (
                                i == 1 and enemyType == 'P' and (
                                (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or (
                                enemyType == 'Q') or (i == 1 and enemyType == 'K'):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check:
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (2, 1), (2, -1), (1, 2), (-1, -2), (1, -2), (-1, 2))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    # get all pawn moves for pawn located at row, col and add those moves to the list
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[r + moveAmount][c] == "--":  # 1 square pawn forward
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(move((r, c), (r + moveAmount, c), self.board))
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":  # 2 square pawn forward
                    moves.append(move((r, c), (r + 2 * moveAmount, c), self.board))

        if c - 1 >= 0:  # Captures to the left
            if not piecePinned or pinDirection == (moveAmount, - 1):  # enemy piece to capture
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(move((r, c), (r + moveAmount, c - 1), self.board))
                if (r + moveAmount, c - 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(kingCol + 1, c - 1)
                            outside_range = range(c + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(kingCol - 1, c, -1)
                            outside_range = range(c - 2, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != "--":  # some piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):  # attacking Piece
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(move((r, c), (r + moveAmount, c - 1), self.board,
                                          isEnPassantMove=True))  # in this case True, bet defaults to False

        if c + 1 <= 7:  # captures to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(move((r, c), (r + moveAmount, c + 1), self.board))
                if (r + moveAmount, c + 1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(kingCol + 1, c)
                            outside_range = range(c + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(kingCol - 1, c + 1, -1)
                            outside_range = range(c - 1, -1, -1)
                        for i in inside_range:
                            if self.board[r][i] != "--":  # some piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(
                            move((r, c), (r + moveAmount, c + 1), self.board, isEnPassantMove=True))  # in this case
                        # True, but defaults to False

    # get all rook moves for rook located at row, col and add those moves to the list
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Ally piece invalid
                            break
                else:  # off board
                    break

    # get all Knight moves for rook located at row, col and add those moves to the list
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, -2), (1, 2), (-1, 2), (-1, -2))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not an Ally piece (empty or enemy piece)
                        moves.append(move((r, c), (endRow, endCol), self.board))

    # get all Bishop moves for rook located at row, col and add those moves to the list
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # Bishop can move maximum of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # On board check
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Ally piece invalid
                            break
                else:  # off board
                    break

    # get all Queen moves for rook located at row, col and add those moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    # get all King moves for rook located at row, col and add those moves to the list
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColour = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour:
                    if allyColour == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(move((r, c), (endRow, endCol), self.board))
                    if allyColour == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    '''
   Generate all valid castle moves for the king at (r,c) and add them to the list of moves
   '''

    def getCastleMoves(self, r, c, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.squareUnderAttack(r, c):
            return  # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":  # no need to check if square is within board
            if (not self.squareUnderAttack(r, c + 1)) and (
                    not self.squareUnderAttack(r, c + 2)):  # squares castled over cannot be under attack
                moves.append(move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            # no need to check if square is within board
            if (not self.squareUnderAttack(r, c - 1)) and (
                    not self.squareUnderAttack(r, c - 2)):  # squares castled over cannot be under attack
                moves.append(move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def playSoundEffects(self):
        MoveMusicFile = r"C:\Users\Mea\Downloads\moveself.mp3"
        CaptureMusicFile = r"C:\Users\Mea\Downloads\capture.mp3"
        if len(self.moveLog) >= 1:
            Move = self.moveLog[-1]
            if Move.pieceCaptured == "--":
                p.mixer.music.load(MoveMusicFile)
                p.mixer.music.play()
            elif Move.pieceCaptured != "--" or Move.isEnpassantMove:
                p.mixer.music.load(CaptureMusicFile)
                p.mixer.music.play()


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # constructor method
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class move:
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # Pawn Promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.isPawnPromotion = True
        # En Passant
        self.isEnpassantMove = isEnPassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        # optional parameter, not every move should be passed in
        if self.pieceMoved[1] == "P" and ((self.endRow, self.endCol) == isEnPassantMove):
            self.isEnpassantMove = True
        # castle move
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # Overriding the str() method
    def __str__(self):
        endSquare = self.getRankFile(self.endRow, self.endCol)
        # castle move
        if self.isCastleMove:
            return "O-O " if self.endCol == 6 else "O-O-O"
            # "O-O"  # King side castle
            # "O-O-O" #queen side castle
        # pawn promotion
        if self.pieceMoved == "wP" and self.endRow == 0:
            return endSquare + "=Q"
        if self.pieceMoved == "bP" and self.endRow == 7:
            return endSquare + "=Q"
        # pawn move
        if self.pieceMoved[1] == "P":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        # other piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare

