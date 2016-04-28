# By Pramod Jacob

## REQUIRED FIXES
## 1) game should pause upon fail - currently flashes for few seconds and resets 

import random, pygame, sys
from pygame.locals import *

# set constants
FPS = 30
WINDOWWIDTH = 800
WINDOWHEIGHT = 900
BOXSIZE = 30
GAPSIZE = 5
FIELDWIDTH = 20
FIELDHEIGHT = 20
XMARGIN = int((WINDOWWIDTH-(FIELDWIDTH*(BOXSIZE+GAPSIZE)))/2)
YMARGIN = XMARGIN
MINESTOTAL = 60

# assertions
assert MINESTOTAL < FIELDHEIGHT*FIELDWIDTH, 'More mines than boxes'
assert BOXSIZE^2 * (FIELDHEIGHT*FIELDWIDTH) < WINDOWHEIGHT*WINDOWWIDTH, 'Boxes will not fit on screen'
assert BOXSIZE/2 > 5, 'Bounding errors when drawing rectangle, cannot use half-5 in drawMinesNumbers'

# assign colors 
LIGHTGRAY = (225, 225, 225)
DARKGRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)

# set up major colors
BGCOLOR = WHITE
FIELDCOLOR = BLACK
BOXCOLOR_COV = DARKGRAY # covered box color
BOXCOLOR_REV = LIGHTGRAY # revealed box color
MINECOLOR = BLACK
TEXTCOLOR_1 = BLUE
TEXTCOLOR_2 = RED
TEXTCOLOR_3 = BLACK
HILITECOLOR = GREEN
RESETBGCOLOR = LIGHTGRAY
MINEMARK_COV = RED

# set up font 
FONTTYPE = 'Courier New'
FONTSIZE = 20

def main():

    # initialize global variables & pygame module, set caption
    global FPSCLOCK, DISPLAYSURFACE, BASICFONT, RESET_SURF, RESET_RECT, SHOW_SURF, SHOW_RECT
    pygame.init()
    pygame.display.set_caption('Minesweeper')
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.SysFont(FONTTYPE, FONTSIZE)

    # obtain reset & show objects and rects
    RESET_SURF, RESET_RECT = drawButton('RESET', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-120)
    SHOW_SURF, SHOW_RECT = drawButton('SHOW ALL', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-95)

    # stores XY of mouse events
    mouse_x = 0
    mouse_y = 0

    # set up data structures and lists
    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

    # set background color
    DISPLAYSURFACE.fill(BGCOLOR)

    # main game loop
    while True:

        # check for quit function
        checkForKeyPress()

        # initialize input booleans
        mouseClicked = False
        spacePressed = False

        # draw field
        DISPLAYSURFACE.fill(BGCOLOR)
        pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (XMARGIN-5, YMARGIN-5, (BOXSIZE+GAPSIZE)*FIELDWIDTH+5, (BOXSIZE+GAPSIZE)*FIELDHEIGHT+5))
        drawField()
        drawMinesNumbers(mineField)        

        # event handling loop
        for event in pygame.event.get(): 
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                terminate()
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouseClicked = True
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    spacePressed = True
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    spacePressed = False

        # draw covers
        drawCovers(revealedBoxes, markedMines)

        # mine marker tip
        tipFont = pygame.font.SysFont(FONTTYPE, 16) ## not using BASICFONT - too big
        drawText('Tip: Highlight a box and press space (rather than click the mouse)', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-60)
        drawText('to mark areas that you think contain mines.', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-40)
            
        # determine boxes at clicked areas
        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)

        # mouse not over a box in field
        if (box_x, box_y) == (None, None):

            # check if reset box is clicked
            if RESET_RECT.collidepoint(mouse_x, mouse_y):
                highlightButton(RESET_RECT)
                if mouseClicked: 
                    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

            # check if show box is clicked
            if SHOW_RECT.collidepoint(mouse_x, mouse_y):
                highlightButton(SHOW_RECT)
                if mouseClicked:
                    revealedBoxes = blankRevealedBoxData(True)

        # mouse currently over box in field
        else:

            # highlight unrevealed box
            if not revealedBoxes[box_x][box_y]: 
                highlightBox(box_x, box_y)

                # mark mines
                if spacePressed:
                    markedMines.append([box_x, box_y])
                    
                # reveal clicked boxes
                if mouseClicked:
                    revealedBoxes[box_x][box_y] = True

                    # when 0 is revealed, show relevant boxes
                    if mineField[box_x][box_y] == '[0]':
                        showNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY)

                    # when mine is revealed, show mines
                    if mineField[box_x][box_y] == '[X]':
                        showMines(revealedBoxes, mineField, box_x, box_y)
                        gameOverAnimation(mineField, revealedBoxes, markedMines, 'LOSS')
                        mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

        # check if player has won 
        if gameWon(revealedBoxes, mineField):
            gameOverAnimation(mineField, revealedBoxes, markedMines, 'WIN')
            mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()
            
        # redraw screen, wait clock tick
        pygame.display.update()
        FPSCLOCK.tick(FPS)
    
def blankField():

   # creates blank FIELDWIDTH x FIELDHEIGHT data structure

    field = []
    for x in range(FIELDWIDTH):
        field.append([]) 
        for y in range(FIELDHEIGHT):
            field[x].append('[ ]')
    return field

def placeMines(field): 

    # places mines in FIELDWIDTH x FIELDHEIGHT data structure
    # requires blank field as input

    mineCount = 0
    xy = [] 
    while mineCount < MINESTOTAL: 
        x = random.randint(0,FIELDWIDTH-1)
        y = random.randint(0,FIELDHEIGHT-1)
        xy.append([x,y]) 
        if xy.count([x,y]) > 1: 
            xy.remove([x,y]) 
        else: 
            field[x][y] = '[X]' 
            mineCount += 1

def isThereMine(field, x, y): 

    # checks if mine is located at specific box on field

    return field[x][y] == '[X]'  

def placeNumbers(field): 

    # places numbers in FIELDWIDTH x FIELDHEIGHT data structure
    # requires field with mines as input

    for x in range(FIELDWIDTH):
        for y in range(FIELDHEIGHT):
            if not isThereMine(field, x, y):
                count = 0
                if x != 0: 
                    if isThereMine(field, x-1, y):
                        count += 1
                    if y != 0: 
                        if isThereMine(field, x-1, y-1):
                            count += 1
                    if y != FIELDHEIGHT-1: 
                        if isThereMine(field, x-1, y+1):
                            count += 1
                if x != FIELDWIDTH-1: 
                    if isThereMine(field, x+1, y):
                        count += 1
                    if y != 0: 
                        if isThereMine(field, x+1, y-1):
                            count += 1
                    if y != FIELDHEIGHT-1: 
                        if isThereMine(field, x+1, y+1):
                            count += 1
                if y != 0: 
                    if isThereMine(field, x, y-1):
                        count += 1
                if y != FIELDHEIGHT-1: 
                    if isThereMine(field, x, y+1):
                        count += 1
                field[x][y] = '[%s]' %(count)

def blankRevealedBoxData(val):

    # returns FIELDWIDTH x FIELDHEIGHT data structure different from the field data structure
    # each item in data structure is boolean (val) to show whether box at those fieldwidth & fieldheight coordinates should be revealed

    revealedBoxes = []
    for i in range(FIELDWIDTH):
        revealedBoxes.append([val] * FIELDHEIGHT)
    return revealedBoxes

def gameSetup():

    # set up mine field data structure, list of all zeros for recursion, and revealed box boolean data structure

    mineField = blankField()
    placeMines(mineField)
    placeNumbers(mineField)
    zeroListXY = []
    markedMines = []
    revealedBoxes = blankRevealedBoxData(False)

    return mineField, zeroListXY, revealedBoxes, markedMines

def drawField():

    # draws field GUI and reset button

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_REV, (left, top, BOXSIZE, BOXSIZE))

    DISPLAYSURFACE.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURFACE.blit(SHOW_SURF, SHOW_RECT)

def drawMinesNumbers(field):
    
    # draws mines and numbers onto GUI
    # field should have mines and numbers

    half = int(BOXSIZE*0.5) 
    quarter = int(BOXSIZE*0.25)
    eighth = int(BOXSIZE*0.125)
    
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            center_x, center_y = getCenterXY(box_x, box_y)
            if field[box_x][box_y] == '[X]':
                pygame.draw.circle(DISPLAYSURFACE, MINECOLOR, (left+half, top+half), quarter)
                pygame.draw.circle(DISPLAYSURFACE, WHITE, (left+half, top+half), eighth)
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+eighth, top+half), (left+half+quarter+eighth, top+half))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+half, top+eighth), (left+half, top+half+quarter+eighth))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+quarter), (left+half+quarter, top+half+quarter))
                pygame.draw.line(DISPLAYSURFACE, MINECOLOR, (left+quarter, top+half+quarter), (left+half+quarter, top+quarter))
            else: 
                for i in range(1,9):
                    if field[box_x][box_y] == '[' + str(i) + ']':
                        if i in range(1,3):
                            textColor = TEXTCOLOR_1
                        else:
                            textColor = TEXTCOLOR_2
                        drawText(str(i), BASICFONT, textColor, DISPLAYSURFACE, center_x, center_y)

def showNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY):

    # modifies revealedBox data strucure if chosen box_x & box_y is [0] 
    # show all boxes using recursion
    
    revealedBoxes[box_x][box_y] = True
    revealAdjacentBoxes(revealedBoxes, box_x, box_y)
    for i,j in getAdjacentBoxesXY(mineField, box_x, box_y):
        if mineField[i][j] == '[0]' and [i,j] not in zeroListXY:
            zeroListXY.append([i,j])
            showNumbers(revealedBoxes, mineField, i, j, zeroListXY)

def showMines(revealedBoxes, mineField, box_x, box_y): 

    # modifies revealedBox data strucure if chosen box_x & box_y is [X] 

    for i in range(FIELDWIDTH):
        for j in range(FIELDHEIGHT):
            if mineField[i][j] == '[X]':
                revealedBoxes[i][j] = True
    
def revealAdjacentBoxes(revealedBoxes, box_x, box_y):

    # modifies revealedBoxes data structure so that all adjacent boxes to (box_x, box_y) are set to True

    if box_x != 0: 
        revealedBoxes[box_x-1][box_y] = True
        if box_y != 0: 
            revealedBoxes[box_x-1][box_y-1] = True
        if box_y != FIELDHEIGHT-1: 
            revealedBoxes[box_x-1][box_y+1] = True
    if box_x != FIELDWIDTH-1:
        revealedBoxes[box_x+1][box_y] = True
        if box_y != 0: 
            revealedBoxes[box_x+1][box_y-1] = True
        if box_y != FIELDHEIGHT-1: 
            revealedBoxes[box_x+1][box_y+1] = True
    if box_y != 0: 
        revealedBoxes[box_x][box_y-1] = True
    if box_y != FIELDHEIGHT-1: 
        revealedBoxes[box_x][box_y+1] = True

def getAdjacentBoxesXY(mineField, box_x, box_y):

    # get box XY coordinates for all adjacent boxes to (box_x, box_y)

    adjacentBoxesXY = []

    if box_x != 0:
        adjacentBoxesXY.append([box_x-1,box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x-1,box_y-1])
        if box_y != FIELDHEIGHT-1:
            adjacentBoxesXY.append([box_x-1,box_y+1])
    if box_x != FIELDWIDTH-1: 
        adjacentBoxesXY.append([box_x+1,box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x+1,box_y-1])
        if box_y != FIELDHEIGHT-1:
            adjacentBoxesXY.append([box_x+1,box_y+1])
    if box_y != 0:
        adjacentBoxesXY.append([box_x,box_y-1])
    if box_y != FIELDHEIGHT-1:
        adjacentBoxesXY.append([box_x,box_y+1])

    return adjacentBoxesXY
    
def drawCovers(revealedBoxes, markedMines):

    # uses revealedBox FIELDWIDTH x FIELDHEIGHT data structure to determine whether to draw box covering mine/number
    # draw red cover instead of gray cover over marked mines

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if not revealedBoxes[box_x][box_y]:
                left, top = getLeftTopXY(box_x, box_y)
                if [box_x, box_y] in markedMines:
                    pygame.draw.rect(DISPLAYSURFACE, MINEMARK_COV, (left, top, BOXSIZE, BOXSIZE))
                else:
                    pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_COV, (left, top, BOXSIZE, BOXSIZE))

def drawText(text, font, color, surface, x, y):  

    # function to easily draw text and also return object & rect pair

    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)

def drawButton(text, color, bgcolor, center_x, center_y):

    # similar to drawText but text has bg color and returns obj & rect

    butSurf = BASICFONT.render(text, True, color, bgcolor)
    butRect = butSurf.get_rect()
    butRect.centerx = center_x
    butRect.centery = center_y

    return (butSurf, butRect)

def getLeftTopXY(box_x, box_y):

    # get left & top coordinates for drawing mine boxes

    left = XMARGIN + box_x*(BOXSIZE+GAPSIZE)
    top = YMARGIN + box_y*(BOXSIZE+GAPSIZE)
    return left, top

def getCenterXY(box_x, box_y):

    # get center coordinates for drawing mine boxes
    
    center_x = XMARGIN + BOXSIZE/2 + box_x*(BOXSIZE+GAPSIZE)
    center_y = YMARGIN + BOXSIZE/2 + box_y*(BOXSIZE+GAPSIZE)
    return center_x, center_y

def getBoxAtPixel(x, y):

    # gets coordinates of box at mouse coordinates
    
    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)

def highlightBox(box_x, box_y):

    # highlight box when mouse hovers over it
    
    left, top = getLeftTopXY(box_x, box_y)
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (left, top, BOXSIZE, BOXSIZE), 4)

def highlightButton(butRect):

    # highlight button when mouse hovers over it

    linewidth = 4
    pygame.draw.rect(DISPLAYSURFACE, HILITECOLOR, (butRect.left-linewidth, butRect.top-linewidth, butRect.width+2*linewidth, butRect.height+2*linewidth), linewidth)

def gameWon(revealedBoxes, mineField):

    # check if player has revealed all boxes

    notMineCount = 0

    for box_x in range(FIELDWIDTH):
        for box_y in range(FIELDHEIGHT):
            if revealedBoxes[box_x][box_y] == True:
                if mineField[box_x][box_y] != '[X]':
                    notMineCount += 1

    if notMineCount >= (FIELDWIDTH*FIELDHEIGHT)-MINESTOTAL:
        return True
    else:
        return False

def gameOverAnimation(mineField, revealedBoxes, markedMines, result):

    # makes background flash red (loss) or blue (win)

    origSurf = DISPLAYSURFACE.copy()
    flashSurf = pygame.Surface(DISPLAYSURFACE.get_size())
    flashSurf = flashSurf.convert_alpha()
    animationSpeed = 20

    if result == 'WIN':
        r, g, b = BLUE
    else:
        r, g, b = RED

    for i in range(5):
        for start, end, step in ((0, 255, 1), (255, 0, -1)):
            for alpha in range(start, end, animationSpeed*step): # animation loop
                checkForKeyPress()
                flashSurf.fill((r, g, b, alpha))
                DISPLAYSURFACE.blit(origSurf, (0, 0))
                DISPLAYSURFACE.blit(flashSurf, (0, 0))
                pygame.draw.rect(DISPLAYSURFACE, FIELDCOLOR, (XMARGIN-5, YMARGIN-5, (BOXSIZE+GAPSIZE)*FIELDWIDTH+5, (BOXSIZE+GAPSIZE)*FIELDHEIGHT+5))
                drawField()
                drawMinesNumbers(mineField)
                tipFont = pygame.font.SysFont(FONTTYPE, 16) ## not using BASICFONT - too big
                drawText('Tip: Highlight a box and press space (rather than click the mouse)', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-60)
                drawText('to mark areas that you think contain mines.', tipFont, TEXTCOLOR_3, DISPLAYSURFACE, WINDOWWIDTH/2, WINDOWHEIGHT-40)
                RESET_SURF, RESET_RECT = drawButton('RESET', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-120)
                SHOW_SURF, SHOW_RECT = drawButton('SHOW ALL', TEXTCOLOR_3, RESETBGCOLOR, WINDOWWIDTH/2, WINDOWHEIGHT-95)
                drawCovers(revealedBoxes, markedMines)
                pygame.display.update()
                FPSCLOCK.tick(FPS)
  
def terminate():

    # simple function to exit game
    
    pygame.quit()
    sys.exit()

def checkForKeyPress():

    # check if quit or any other key is pressed
    
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
        
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

# run code
if __name__ == '__main__':
    main()
