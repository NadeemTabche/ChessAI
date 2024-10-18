import pygame as p
import subprocess
import sys
import webbrowser
import random

# Initialize Pygame
p.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (169, 169, 169)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 36
FONT_NAME = 'Times New Roman'
BUTTON_RADIUS = 10
# Load the gear icon image
gearIcon = p.image.load("UI Images/gear_icon.png")
gearIcon = p.transform.scale(gearIcon, (30, 30))  # Adjust size as needed


# Function to display text on the screen
def drawText(surface, text, size, color, x, y, fontName):
    font = p.font.SysFont(fontName, size)
    textSurface = font.render(text, True, color)
    textRect = textSurface.get_rect(center=(x, y))
    surface.blit(textSurface, textRect)


# Function to create rounded buttons
def createButton(surface, text, x, y, width, height, color, hoverColor, action=None, icon=None, font=None):
    mouse = p.mouse.get_pos()
    click = p.mouse.get_pressed()

    rect = p.Rect(x, y, width, height)
    p.draw.rect(surface, color, rect, border_radius=BUTTON_RADIUS)

    if rect.collidepoint(mouse):
        p.draw.rect(surface, hoverColor, rect, border_radius=BUTTON_RADIUS)
        if click[0] == 1 and action is not None:
            action()

    if icon:
        surface.blit(icon, (x + 5, y + 5))

    if font:
        textSurface = font.render(text, True, WHITE)
        textRect = textSurface.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(textSurface, textRect)

# Function to create static buttons (toggles)
def createStaticButton(surface, text, x, y, width, height, color, hoverColor, action=None, icon=None, font=None):
    mouse = p.mouse.get_pos()
    click = p.mouse.get_pressed()

    rect = p.Rect(x, y, width, height)

    buttonClicked = False

    if rect.collidepoint(mouse):
        p.draw.rect(surface, hoverColor, rect, border_radius=BUTTON_RADIUS)
        if click[0] == 1 and action is not None:
            action()
            buttonClicked = True
    else:
        p.draw.rect(surface, color, rect, border_radius=BUTTON_RADIUS)

    if icon:
        surface.blit(icon, (x + 5, y + 5))

    if font:
        textSurface = font.render(text, True, WHITE)
        textRect = textSurface.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(textSurface, textRect)

    return buttonClicked


startScreenImage = p.image.load("images\logo.png")  # 600/360 ≈ 1.67/1
startScreenImage = p.transform.scale(startScreenImage, (334, 200))  # scale according to dimension ratio
# Function to handle the welcome menu
def welcomeMenu():
    welcomeScreen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess AI")

    clock = p.time.Clock()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()
            welcomeScreen.fill(BLACK)
            welcomeScreen.blit(startScreenImage, (235, 0))  # logo positioning
            drawText(welcomeScreen, "Chess AI", 72, WHITE, WIDTH // 2, HEIGHT // 3, FONT_NAME)

            createButton(welcomeScreen, "Start", WIDTH // 2 - 75, HEIGHT // 2, 150, 50, GREY, GREEN,
                         mainMenu, font=p.font.SysFont(FONT_NAME, FONT_SIZE))

            createButton(welcomeScreen, "Tutorial Menu", WIDTH // 2 - 125, HEIGHT // 3 + 200, 250, 50, GREY,
                         (100, 100, 100),
                         tutorialMenu, font=p.font.SysFont(FONT_NAME, FONT_SIZE))
            p.display.flip()
            clock.tick(FPS)


# Function to handle the main menu
def mainMenu():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess AI")

    clock = p.time.Clock()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit()

        # Additional event handling logic for other events if needed
        screen.fill(BLACK)
        drawText(screen, "Main Menu", 50, WHITE, 400, 70, "timesnewroman")

        createButton(screen, "Play against Human", 250, 150, 300, 50, GREY, (100, 100, 100), playHuman,
                     font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createButton(screen, "Play against AI", 250, 250, 300, 50, GREY, (100, 100, 100), playAI,
                     font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createButton(screen, "AI vs AI", 250, 350, 300, 50, GREY, (100, 100, 100), AIVsAI,
                     font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createButton(screen, "Back To Start", WIDTH // 2 - 150, HEIGHT // 3 + 250, 300, 50, RED,
                     (100, 100, 100),
                     welcomeMenu, font=p.font.SysFont(FONT_NAME, FONT_SIZE))

        # Display settings button as a gear icon in the top left corner
        createButton(screen, "", 10, 10, 40, 40, BLACK, BLACK, settings, gearIcon)

        p.display.flip()
        clock.tick(FPS)
        p.time.delay(10)  # Add a small delay to avoid running the loop too fast


def playHuman():  # Function to handle the play against human option
    # Run ChessMain.py
    subprocess.run(["python", "ChessMain.py", "0", "0", "ON" if easyAIvar else "OFF", "1" if highlightingVar else "0",
                    "1" if soundEffectsVar else "0", str(randomNum)])


def playAI():  # Function to handle the play against AI option
    # Run ChessMain.py
    subprocess.run(["python", "ChessMain.py", "0", "1", "ON" if easyAIvar else "OFF", "1" if highlightingVar else "0",
                    "1" if soundEffectsVar else "0", str(randomNum)])


def AIVsAI():  # Function to handle the AI vs AI option
    # Run ChessMain.py
    subprocess.run(["python", "ChessMain.py", "1", "1", "ON" if easyAIvar else "OFF", "1" if highlightingVar else "0",
                    "1" if soundEffectsVar else "0", str(randomNum)])


# Function to handle the settings option
def settings():
    settingsScreen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Settings")

    clock = p.time.Clock()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                exit()

        settingsScreen.fill(BLACK)

        drawText(settingsScreen, "Settings", 50, WHITE, 400, 70, "timesnewroman")

        createStaticButton(settingsScreen, "EasyAI", 40, 175, 300, 50, GREEN if easyAIvar else RED, (100, 100, 100),
                           easyAI,
                           font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createStaticButton(settingsScreen, "Highlighting", 460, 175, 300, 50, GREEN if highlightingVar else RED,
                           (100, 100, 100), highlighting,
                           font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createStaticButton(settingsScreen, "Sound Effects", 40, 310, 300, 50, GREEN if soundEffectsVar else RED,
                           (100, 100, 100), soundEffects,
                           font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createStaticButton(settingsScreen, "Random Colour", 460, 310, 300, 50, buttonColour, buttonColour,
                           randomBoardColour,
                           font=p.font.SysFont(FONT_NAME, FONT_SIZE))

        createStaticButton(settingsScreen, "Back to Main Menu", 250, 500, 300, 50, GREY, (100, 100, 100), mainMenu,
                           font=p.font.SysFont(FONT_NAME, FONT_SIZE))

        p.display.flip()
        clock.tick(FPS)


easyAIvar = False
def easyAI():
    global easyAIvar
    p.time.delay(100)
    easyAIvar = not easyAIvar
    print("Easy AI state:", easyAIvar)


highlightingVar = True
# drawText(surface, text, size, color, x, y, fontName)
def highlighting():
    global highlightingVar
    p.time.delay(100)
    highlightingVar = not highlightingVar
    print("Highlighting state:", highlightingVar)


soundEffectsVar = True
def soundEffects():
    global soundEffectsVar
    p.time.delay(100)
    soundEffectsVar = not soundEffectsVar
    print("Sound Effects state:", soundEffectsVar)


randomNum = 0
def randomBoardColour():
    global randomNum
    randomNum = random.randint(0, 6)
    p.time.delay(100)
    print("random Colour (R, G, B):", buttonColour)
    randomBoardColourButton()


BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GREEN = (1, 50, 32)
PINK = (255, 192, 203)
MAGENTA = (255, 0, 255)

buttonColour = GREY
def randomBoardColourButton():
    global buttonColour
    if randomNum == 0:
        buttonColour = GREY
    elif randomNum == 1:
        buttonColour = BLUE
    elif randomNum == 2:
        buttonColour = RED
    elif randomNum == 3:
        buttonColour = YELLOW
    elif randomNum == 4:
        buttonColour = DARK_GREEN
    elif randomNum == 5:
        buttonColour = PINK
    elif randomNum == 6:
        buttonColour = MAGENTA


def openVideos():
    TutorialFolderLink = "https://drive.google.com/drive/folders/1gBk4RPaApcmKUqC3KdsU3uGv13Pf74UJ?usp=sharing"
    p.time.delay(60)  # add a small delay to avoid accidentally spamming in new tabs
    webbrowser.open(TutorialFolderLink)


def tutorialMenu():
    tutorialScreen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Tutorial")

    clock = p.time.Clock()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                exit()

        tutorialScreen.fill(BLACK)
        drawText(tutorialScreen, "Tutorial Menu", 50, WHITE, 400, 70, "timesnewroman")
        drawText(tutorialScreen, "Game Controls:", 30, WHITE, 400, 320, "timesnewroman")
        drawText(tutorialScreen, "Press U to UNDO a Move    ", 25, WHITE, 400, 365, "timesnewroman")
        drawText(tutorialScreen, "Press R to RESET the Board", 25, WHITE, 400, 395, "timesnewroman")

        createButton(tutorialScreen, "Back to Main Menu", 250, 500, 300, 50, GREY, (100, 100, 100), mainMenu,
                     font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createButton(tutorialScreen, "Tutorial Video Playlist", 225, 200, 350, 50, RED, (100, 100, 100), openVideos,
                     font=p.font.SysFont(FONT_NAME, FONT_SIZE))
        createButton(tutorialScreen, "", 10, 10, 40, 40, BLACK, BLACK, settings, gearIcon)

        p.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    welcomeMenu()
