"""
this is our main driver file. It will be responsible for handling user input and
displaying the current GameState object
"""
import pygame as p
import sys
from Chess import ChessEngine, AI
from multiprocessing import Process, Queue
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Stops Pygame Welcome Message from popping up after every AI move

# click and drag
# 3 move repeating draw
# choosing AI difficulty
# choosing AI

boardWidth = boardHeight = 512
moveLogPanelWidth = 400
moveLogPanelHeight = boardHeight
dimension = 8
sq_size = boardHeight // dimension
max_fps = 15
images = {}
'''
Initialise a global dictionary of images. This will be called exactly once in the main
'''
playerOne = 0
playerTwo = 1
HighlightSquaresUI = None
soundEffects = None
BoardColour = None
# Check if command-line arguments are provided
if len(sys.argv) > 1:
    # the first argument is playerOne and the second is playerTwo
    playerOne = int(sys.argv[1])
    playerTwo = int(sys.argv[2])
    EasyDepthUI = str(sys.argv[3])
    HighlightSquaresUI = int(sys.argv[4])
    soundEffects = int(sys.argv[5])
    BoardColour = int(sys.argv[6])


def loadimages():
    pieceID = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieceID:
        images[piece] = p.image.load("images/" + piece + ".png")


# Note: we can access an image by saying images["wP"]
'''
The main driver for our code. This will handle user input and updating the graphics.'''


def main():
    global playerOne, playerTwo, returnQueue
    p.init()
    screen = p.display.set_mode((boardWidth + moveLogPanelWidth, boardHeight))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Times New Roman", 14, False, False)
    gs = ChessEngine.Gamestate()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    loadimages()  # only do this once, before while loop
    running = True
    sqSelected = ()  # no square is selected initially, keep track of the last click of the user (tuple: (row,col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False
    AIThinking = False
    AIProcess = None
    moveUndone = False
    while running:
        isHuman = (gs.whiteToMove and playerOne == 0) or (not gs.whiteToMove and playerTwo == 0)
        if (playerOne == 0 and playerTwo == 1) or (playerOne == 1 and playerTwo == 0):
            p.display.set_caption("Player Vs. AI")
        elif playerOne == 0 and playerTwo == 0:
            p.display.set_caption("Player Vs. Player")
        elif playerOne == 1 and playerTwo == 1:
            p.display.set_caption("AI Vs. AI")
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y) location of mouse
                    col = location[0] // sq_size
                    row = location[1] // sq_size
                    if sqSelected == (row, col) or col > 7:  # user clicked same square twice or user clicked move log
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both first and second clicks
                    if len(playerClicks) == 2 and isHuman:  # after 2nd click
                        move = ChessEngine.move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # keyboard handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        AIProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:
                    gs = ChessEngine.Gamestate()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        AIProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        # AI move finder
        if not gameOver and not isHuman and (not moveUndone or ((playerOne and playerTwo) == 1)):
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # used to pass data between threads
                AIProcess = Process(target=AI.initialiseNegaMaxAlphaBeta, args=(gs, validMoves, returnQueue))
                AIProcess.start()  # Call AI.initialiseNegaMaxAlphaBeta(gs, validMoves, returnQueue)

            if not AIProcess.is_alive():  # checking if thread is still alive
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = AI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)  # animate last move made
            if soundEffects == 1:
                gs.playSoundEffects()
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black Wins by Checkmate")
            else:
                drawEndGameText(screen, "White wins by Checkmate")
        elif gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Draw by Stalemate")
        elif gs.threeMoveDrawRule:
            gameOver = True
            drawEndGameText(screen, "Draw by Three Move Rule")
        elif gs.fiftyMoveDrawRule:
            gameOver = True
            drawEndGameText(screen, "Draw by Fifty Move Draw Rule")

        clock.tick(max_fps)
        p.display.flip()


'''
responsible for all the graphics within a current GameState
'''

'''Highlight square selected and moves for piece selected'''


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    global HighlightSquaresUI
    drawBoard(screen)  # draw squares on the board
    if HighlightSquaresUI != 0:
        highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares
    drawMoveLog(screen, gs, moveLogFont)
    
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(boardWidth, 0, moveLogPanelWidth, moveLogPanelHeight)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = (" " + str(i // 2 + 1) + ". " + str(moveLog[i]) + " ")
        if i + 1 < len(moveLog):
            moveString += str(moveLog[i + 1])
        moveTexts.append(moveString)
    if gs.inCheck:
        if gs.checkMate:
            moveTexts.append("#")  # put up a hashtag for checkmate
        else:
            moveTexts.append("+")  # put up a plus for checkmate
    movesPerRow = 4
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):  # adds every movesPerRow move pairs before moving row on moveLog
            if i + j < len(moveTexts):
                text += moveTexts[i + j]
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)  # horizontal and vertical padding
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


MAGENTA = (255, 20, 255)

def drawBoard(screen):
    global BoardColour
    global colors  # we need to use the variable in animateMove function
    if BoardColour == 0:
        colors = [p.Color("white"), p.Color("grey")]
    elif BoardColour == 1:
        colors = [p.Color("white"), p.Color("blue")]
    elif BoardColour == 2:
        colors = [p.Color("white"), p.Color("red")]
    elif BoardColour == 3:
        colors = [p.Color("white"), p.Color("yellow")]
    elif BoardColour == 4:
        colors = [p.Color("white"), p.Color("dark green")]
    elif BoardColour == 5:
        colors = [p.Color("white"), p.Color("pink")]
    elif BoardColour == 6:
        colors = [p.Color("white"), p.Color(MAGENTA)]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))


def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))


def highlightSquares(screen, gs, validMoves, sqSelected):
    global playerOne, playerTwo
    if not ((playerOne != 0) and (playerTwo != 0)):  # Checks if at least one player is human
        if (len(gs.moveLog)) > 0:
            lastMove = gs.moveLog[-1]
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100)
            s.fill(p.Color('dark green'))
            screen.blit(s, (lastMove.endCol * sq_size, lastMove.endRow * sq_size))

    if sqSelected != ():  # There is a square to select
        (r, c) = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # square selected is a piece that can be moved
            # Highlight selected square
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100)  # adds transparency value
            s.fill(p.Color('blue'))
            screen.blit(s, (c * sq_size, r * sq_size))
            # Highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * sq_size, move.endRow * sq_size))

    if not ((playerOne != 0) and (playerTwo != 0)):  # Checks if at least one player is human
        if gs.inCheck:
            if gs.whiteToMove:  # highlight king square red if king is in check
                    q = p.Surface((sq_size, sq_size))
                    q.fill(p.Color('red'))
                    screen.blit(q, (gs.whiteKingLocation[1] * sq_size, gs.whiteKingLocation[0] * sq_size))
            else:
                    q = p.Surface((sq_size, sq_size))
                    q.fill(p.Color('red'))
                    screen.blit(q, (gs.blackKingLocation[1] * sq_size, gs.blackKingLocation[0] * sq_size))


def animateMove(move, screen, board, clock):
    global playerOne, playerTwo
    dr = move.endRow - move.startRow  # change in row
    dc = move.endCol - move.startCol  # change in column
    framesPerSquare = 6  # frames to move one square
    if (playerOne != 0) and (playerTwo != 0):
        framesPerSquare = 10
    frameCount = (abs(dr) + abs(dc)) * framesPerSquare  # total number of frames
    for frame in range(frameCount + 1):  # plus one actually puts as at the end of the way through
        r, c = (move.startRow + (dr * (frame / frameCount)),
                move.startCol + (dc * (frame / frameCount)))  # dr is change in row but frame in frameCount is the
        # proportion of the way there we are, this makes sure that the image moves bit by bit (talk about vectors)
        drawBoard(screen)  # draw at each frame
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[((move.endRow + move.endCol) % 2)]
        endSquare = p.Rect(move.endCol * sq_size, move.endRow * sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                EnpassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * sq_size, EnpassantRow * sq_size, sq_size, sq_size)
            screen.blit(images[move.pieceCaptured], endSquare)
        # draw moving piece
        if move.pieceMoved != "--":
            screen.blit(images[move.pieceMoved], p.Rect(c * sq_size, r * sq_size, sq_size, sq_size))
        p.display.flip()  # we need this, or we won't see it until final animation
        clock.tick(60)  # control frame rate for animation


def drawEndGameText(screen, text):
    font = p.font.SysFont("Times New Roman", 32, True, False)  # bold not italicised
    textObject = font.render(text, 0, p.Color("purple"))
    textLocation = p.Rect(0, 0, boardWidth, boardHeight).move((boardWidth - textObject.get_width()) / 2,
                                                              (boardHeight - textObject.get_height()) / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(1, 1))


if __name__ == "__main__":
    main()
