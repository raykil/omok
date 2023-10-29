import pygame
import numpy as np
import awkward as ak
from sys import exit

pygame.init()

class Screen:
    def __init__(self, width, height):
        self.width   = width
        self.height  = height
        self.clock   = pygame.time.Clock()
    
    def DisplayScreen(self, board):
            self.screen_size = np.array([self.width, self.height])
            self.screen = pygame.display.set_mode(self.screen_size)
            pygame.display.set_caption("Omok")
            self.screen.fill('gray17')
            board.DisplayBoard()
            board.PlaceStone(np.array([board.nCell//2,board.nCell//2]))
            while True:
                for event in pygame.event.get():
                    if event.type==pygame.QUIT:
                        pygame.quit()
                        exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: 
                            self.gridloc = np.array(np.round(np.array(pygame.mouse.get_pos())/board.unit)-3,dtype=int) # gridloc is an array that represents the grid location of blocks according to the text written on the board.
                            if (self.gridloc[1] >= 15)|(self.gridloc[0] >= 15)|(self.gridloc[1] < 0)|(self.gridloc[0] < 0): print("Selected location is outside the grid.")
                            elif not board.StoneTracker[self.gridloc[1]][self.gridloc[0]]: 
                                board.PlaceStone(self.gridloc)
                                board.IsTerminal()
                            else: print("Stone already exists. Place it somewhere else.")

                self.screen.blit(board.board, tuple((self.screen_size-board.width)/2))
                pygame.display.update()
                self.clock.tick(24)

class Board:
    def __init__(self, screen, nCell=15):
        self.width   = screen.width * 0.9
        self.height  = screen.height * 0.9
        self.counter = 0
        self.boardside = min(self.width, self.height)
        self.board = pygame.Surface((self.boardside, self.boardside))
        self.unit = self.boardside/(nCell+3)
        self.nCell = nCell
        self.StoneTracker = np.full((nCell, nCell), 0, dtype=int) # 0==empty, 1==black, -1==white
        self.EventTracker = ak.Array([])

    def DisplayBoard(self):
        background = pygame.image.load("/Users/raymondkil/Desktop/omok/boardbg.jpg")
        self.board.blit(background,(0,0))
        for n in range(self.nCell):
            pygame.draw.line(self.board, 'grey8', (2.0*self.unit, (2.0+n)*self.unit), (self.boardside-2.0*self.unit, (2.0+n)*self.unit), width=2) # row
            pygame.draw.line(self.board, 'grey8', ((2.0+n)*self.unit, 2.0*self.unit), ((2.0+n)*self.unit, self.boardside-2.0*self.unit), width=2) # col

            coordfont = pygame.font.Font(None, int(0.8*self.unit))
            coords = coordfont.render(str(n), True, 'lightsalmon4')
            self.board.blit(coords,(1.1*self.unit, (1.8+n)*self.unit)) # row
            self.board.blit(coords,((1.7+n)*self.unit, 1.2*self.unit)) # col

        pygame.draw.circle(self.board, 'grey8', ((self.nCell-10)*self.unit, (self.nCell-10)*self.unit), radius=5)
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-10)*self.unit, (self.nCell-2 )*self.unit), radius=5)
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-2 )*self.unit, (self.nCell-10)*self.unit), radius=5)
        pygame.draw.circle(self.board, 'grey8', ((self.nCell-2 )*self.unit, (self.nCell-2 )*self.unit), radius=5)

    def PlaceStone(self, gridloc): # gridloc to be entered as gridvals
        self.StoneTracker[gridloc[1]][gridloc[0]] = 1-2*(len(self.EventTracker)%2) # 1 for black, -1 for white
        self.EventTracker = ak.concatenate((self.EventTracker, [gridloc]), axis=0)
        self.colors = ['grey97','grey8']
        pygame.draw.circle(self.board, self.colors[(len(self.EventTracker))%2], (gridloc+2)*40, radius=16)

        self.counterfont = pygame.font.Font(None, int(0.8*self.unit))
        self.countprint = self.counterfont.render(f"count: {len(self.EventTracker)}", True, 'grey8')
        self.board.blit(self.countprint,(0.5*self.boardside, 0.05*self.boardside))

    def IsTerminal(self):
        minstone, maxstone = (min(self.EventTracker[:,0]), min(self.EventTracker[:,1])), (max(self.EventTracker[:,0]), max(self.EventTracker[:,1]))
        if ((maxstone[0] - minstone[0] >= 4) | (maxstone[1] - minstone[1] >= 4))&(len(self.EventTracker) >= 9):
            laststone = self.EventTracker[-1]
            terminal_state = False
            # Can optimize more by not looking at some states. 
            # Ex) check if testframe has same colored stone on first & last row, if not, do not check the col state.
            # but this seems to have more booleans to check... Maybe it is pretty much fully optimized.
            for r in range(laststone[0]-2,laststone[0]+3):
                if terminal_state: break
                for c in range(laststone[1]-2,laststone[1]+3):
                    testframe = self.StoneTracker[c-2:c+3,r-2:r+3]
                    rowtest = np.sum(testframe, axis=1)
                    coltest = np.sum(np.transpose(testframe), axis=1)
                    di1test = np.trace(testframe)
                    di2test = np.trace(np.fliplr(testframe))
                    if (5 in rowtest)|(5 in coltest)|(5 == di1test)|(5 == di2test): 
                        print("Terminal state. Black won!")
                        terminal_font = pygame.font.Font(None, 40)
                        terminal_state = terminal_font.render("Terminal state. Black won!", True, "firebrick2")
                        self.board.blit(terminal_state,(5*self.unit, 17*self.unit))
                        break
                    elif (-5 in rowtest)|(-5 in coltest)|(-5 == di1test)|(-5 == di2test): 
                        print("Terminal state. White won!")
                        terminal_font = pygame.font.Font(None, 40)
                        terminal_state = terminal_font.render("Terminal state. White won!", True, "firebrick2")
                        self.board.blit(terminal_state,(5*self.unit, 17*self.unit))
                        break



    #def MiniMax(self, StoneTracker, depth): # tells the score of current board
        # Max(black) = 5, Min(white) = -5.


    # def erase:
        # initialize a deleting button.
        # erase the most recent stone.
        # erase the counter. Back one.

screen = Screen(800,800)
board = Board(screen, nCell=15)
screen.DisplayScreen(board)