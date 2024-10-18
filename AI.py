import sys
# RANDOM MOVE AI (1st Model)
import random

pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}  # Dictionary assigns value to each respective piece type

#  knight is generally better in centre than corners
#  helping AI develop positional awareness

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

BishopScores = [[0, 2, 2, 2, 2, 2, 2, 0],
                [2, 4, 4, 4, 4, 4, 4, 2],
                [2, 4, 5, 6, 6, 5, 4, 2],
                [2, 5, 5, 6, 6, 5, 5, 2],
                [2, 4, 6, 6, 6, 6, 4, 2],
                [2, 6, 6, 6, 6, 6, 6, 2],
                [2, 5, 4, 4, 4, 4, 5, 2],
                [0, 2, 2, 2, 2, 2, 2, 0]]

RookScores = [[2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5],
              [5, 7.5, 7.5, 7.5, 7.5, 7.5, 7.5, 5],
              [0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0],
              [0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0],
              [0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0],
              [0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0],
              [0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 0],
              [4, 2.5, 2.5, 5, 5, 2.5, 2.5, 4]]

QueenScores = [[0, 2, 2, 3, 3, 2, 2, 0],
               [2, 4, 4, 4, 4, 4, 4, 2],
               [2, 4, 5, 5, 5, 5, 4, 2],
               [3, 4, 5, 5, 5, 5, 4, 3],
               [4, 4, 5, 5, 5, 5, 4, 3],
               [2, 5, 5, 5, 5, 5, 4, 2],
               [2, 4, 5, 4, 4, 4, 4, 2],
               [0, 2, 2, 3, 3, 2, 2, 0]]

PawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
              [7, 7, 7, 7, 7, 7, 7, 7],
              [3, 3, 4, 5, 5, 4, 3, 3],
              [2.5, 2.5, 3, 4.5, 4.5, 3, 2.5, 2.5],
              [2, 2, 2, 4, 4, 2, 2, 2],
              [2.5, 1.5, 1, 2, 2, 1, 1.5, 2.5],
              [2.5, 3, 3, 0, 0, 3, 3, 2.5],
              [2, 2, 2, 2, 2, 2, 2, 2]]

# [::-1] go through list in reverse order (used for scores from black's perspective
piecePositionScores = {"wN": knightScores, "bN": knightScores[::-1], "wB": BishopScores, "bB": BishopScores[::-1],
                       "wQ": QueenScores, "bQ": QueenScores[::-1], "wR": RookScores, "bR": RookScores[::-1],
                       "wP": PawnScores, "bP": PawnScores[::-1]}

CHECKMATE = 1000  # best possible scenario
STALEMATE = 0  # better than losing position but worse than winning position
EasyDepthUI = 0
# Check if command-line arguments are provided
if len(sys.argv) > 1:
    # the first argument is playerOne and the second is playerTwo
    playerOne = int(sys.argv[1])
    playerTwo = int(sys.argv[2])
    EasyDepthUI = str(sys.argv[3])
    HighlightSquaresUI = int(sys.argv[4])
    soundEffects = int(sys.argv[5])
    BoardColour = int(sys.argv[6])

if EasyDepthUI == "ON":
    maxDepth = 1
else:
    maxDepth = 3
# Check if command-line arguments are provided
'''Picks and returns a random move'''


def findRandomMove(validMoves):
    return random.choice(validMoves)  # Inclusive so we need -1


# Greedy Algorithm (2nd Model)
# Concerned only with winning material (or keeping most material)
def findGreedyMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE  # best score for white, worst for black #trying to minimise opponents best move (max score)
    greedyPlayerMove = None
    random.shuffle(validMoves)  # shuffles moves, adding variety
    for playerMove in validMoves:  # MiniMax without recursion
        # find max opponents response to each move
        gs.makeMove(playerMove)
        # finding opponent's Maximum
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.makeMove(opponentsMove)
            if gs.checkMate:
                score = -turnMultiplier * CHECKMATE
            elif gs.staleMate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            # greedy algorithm
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
            # end
        # if opponent max score is less than previous best score, then that becomes new best move
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            greedyPlayerMove = playerMove
        gs.undoMove()  # so that after it has considered a move, it does not play each one until it finds the greedy one
    return greedyPlayerMove


def initialiseMinMax(gs, validMoves):  # helper method that calls initial recursive call
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    MinMax(gs, validMoves, maxDepth, gs.whiteToMove)
    return nextMove


def initialiseNegaMax(gs, validMoves):  # helper method that calls initial recursive call
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    NegaMax(gs, validMoves, maxDepth, 1 if gs.whiteToMove else -1)
    return nextMove


def initialiseNegaMaxAlphaBeta(gs, validMoves, returnQueue):  # helper method that calls initial recursive call
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    NegaMaxAlphaBeta(gs, validMoves, maxDepth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)


def MinMax(gs, validMoves, depth, BoolwhiteToMove):  # recursive algorithm
    global nextMove
    if depth == 0:  # base case
        return scoreMaterial(gs.board)

    if BoolwhiteToMove:  # Maximise (white)
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = MinMax(gs, nextMoves, depth - 1, not BoolwhiteToMove)
            if score > maxScore:  # find updated Max
                maxScore = score
                if depth == maxDepth:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:  # Minimise (black)
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = MinMax(gs, nextMoves, depth - 1, BoolwhiteToMove)
            if score < minScore:  # find updated Min
                minScore = score
                if depth == maxDepth:
                    nextMove = move
            gs.undoMove()
        return minScore


def NegaMax(gs, validMoves, depth, turnMultiplier):  # always look for max but negate on blacks turn
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -(NegaMax(gs, nextMoves, depth - 1, -turnMultiplier))
        if score > maxScore:  # find updated Max
            maxScore = score
            if depth == maxDepth:
                nextMove = move
        gs.undoMove()
    return maxScore


def NegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta,
                     turnMultiplier):  # always look for max but negate on blacks turn
    # alpha is upper bound
    # beta is lower bound
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    # move ordering best-first
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -1 * NegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:  # find updated Max
            maxScore = score
            if depth == maxDepth:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:  # pruning
            alpha = maxScore
        if alpha >= beta:
            break
    if gs.staleMate or gs.threeMoveDrawRule or gs.fiftyMoveDrawRule:
        maxScore = 0
    return maxScore


'''
Positive is good for white, negative is good for black
'''


def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black Wins
        else:
            return CHECKMATE
    elif gs.staleMate or gs.fiftyMoveDrawRule or gs.threeMoveDrawRule:
        return STALEMATE

    score = 0
    weight = 0.1
    for r in range(len(gs.board)):
        for c in range(len(gs.board[r])):
            square = gs.board[r][c]
            if square != "--":  # check that there is a piece
                # score positionally
                piecePositionScore = 0
                if square[1] != "K":
                    piecePositionScore = piecePositionScores[square][r][c]  # return number in Score tables
                if square[0] == "w":
                    score += (pieceScore[square[1]] + (piecePositionScore * weight))
                elif square[0] == "b":
                    score -= (pieceScore[square[1]] + (piecePositionScore * weight))
    return score


'''Score Board based on material'''


def scoreMaterial(board):
    score = 0
    for r in board:
        for square in r:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score
