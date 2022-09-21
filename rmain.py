import pygame, sys

clock = pygame.time.Clock()

from pygame.locals import *
pygame.init()

pygame.display.set_caption('rush hour')

s_width = 684
s_height = 720

screen = pygame.display.set_mode((s_width,s_height))

#each tile is 6x6 pixels, multiply by 12 for scale
#car = 6x12, truck = 6x18
#grid coords: tl = (126,72); tr = (486,72); bl = (126,432); br = (486,432)


colors = {'red':(163,0,0), 'yellow':(227,232,69), 'lime':(100,180,0), 'blue':(0,21,156), 'black':(15,15,15),'grey':(170,170,170),
          'purple':(155,0,255), 'brown':(110,50,0), 'green':(0,110,0), 'sky':(106,245,245), 'salmon':(250,128,114)}

Tcolors = {'Torange':(212,90,8), 'Tpink':(250,123,231), 'Tobi':(27,0,54), 'Tcyan':(0,151,151)}

outline = pygame.image.load("sprites/outline.png")
rush = pygame.image.load("sprites/rush.png")
hour = pygame.image.load("sprites/hour.png")
background = pygame.image.load("background.jpeg")
board = pygame.transform.scale(pygame.image.load('sprites/gameboard.png'), (480,480))

board_rect = pygame.Rect(126,72, 72*6, 72*6)
r_pos = [0 - rush.get_width(), 100]
h_pos = [s_width, r_pos[1] + rush.get_height() + 60]

restart = pygame.image.load("buttons/restart.png")
nxt = pygame.image.load("buttons/next.png")
home = pygame.image.load("buttons/home.png")

restart_rect = restart.get_rect()
nxt_rect = nxt.get_rect()
home_rect = home.get_rect()

gamestart = False
touching_r = False
touching_n = False
touching_h = False

level = 1

class Car:
    def __init__(self, x, y, color, dir_):
        self.x = 126 + x*72
        self.y = 72 + y*72
        self.color = color
        self.dir = dir_
        if self.dir == 'v':
            self.width = 72
            self.height = 144
        else:
            self.width = 144
            self.height = 72
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def logic(self, tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck):
        if self.rect not in vehicle_rects:
            vehicle_rects.append(self.rect)
            
        if tile not in coloring:
            coloring.append(tile)
            
        if self.rect == selected_rect:
            selected_dir = self.dir
            selected_c = self.color
            is_truck = False

        return vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck

class Truck:
    def __init__(self, x, y, color, dir_):
        self.x = 126 + x*72
        self.y = 72 + y*72
        self.color = color
        self.dir = dir_
        if self.dir == 'v':
            self.width = 72
            self.height = 216
        else:
            self.width = 216
            self.height = 72
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def logic(self, tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck):
        if self.rect not in vehicle_rects:
            vehicle_rects.append(self.rect)
            
        if tile not in coloring:
            coloring.append(tile)
            
        if self.rect == selected_rect:
            selected_dir = self.dir
            selected_c = self.color
            is_truck = True

        return vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck

def file(level):
    grid = []
    lvl = []
    if level != 8:
        a = str(level)
    else:
        a = '8(29)'
    
    f = open("levels/" + a + '.txt' , 'r')
    data = f.read()
    f.close()
    data = data.split('\n') #this new version of data is a list
    
    for row in data:
        grid.append(list(row))
            
    return grid
    

def reset(restart_rect, nxt_rect, home_rect, level):
    global selected_rect, selected_dir, selected_c, dir_, grid, selected, is_truck, vehicle_rects, blit_list, coloring, endtick, moves, complete, gameend, c, velo

    grid = file(level)

    selected_rect = pygame.Rect(0,0,0,0)
    selected_dir = ''
    selected_c = ''
    dir_ = 'a'

    selected = False
    is_truck = False
    complete = False
    gameend = False

    blit_list = []
    coloring = []
    vehicle_rects = []

    endtick = 0
    moves = 0

    restart_rect.center = (600,605)
    nxt_rect.center = (-100,-100)
    home_rect.center = (50, 50)

    c = 0
    velo = 0

    
    return restart_rect, nxt_rect, home_rect


def pregame(gamestart, r_pos, h_pos, rush, hour, c):
    h = False
    p = False

#rush animation   
    if r_pos[0] <= s_width/2 - rush.get_width():
        r_pos[0] += 8
    elif r_pos[0] >= s_width/2 - rush.get_width():
        h = True

#hour animation
    if h_pos[0] >= s_width/2 - hour.get_width() and h == True:
        h_pos[0] -= 8
    elif h_pos[0] <= s_width/2 - hour.get_width():
        c += 1
        
    screen.blit(pygame.transform.scale(rush, (rush.get_width() * 2, rush.get_height() * 2)), (r_pos[0], r_pos[1]))
    screen.blit(pygame.transform.scale(hour, (hour.get_width() * 2, hour.get_height() * 2)), (h_pos[0], h_pos[1]))
    
    if c > 41:
        p = pygame.mouse.get_pressed()[0]
    
    font = pygame.font.Font('font.ttf', 40)

    text = font.render('Click anywhere to begin', True, (0,0,0))

    if c % 80 >= 41:
        screen.blit(text, (s_width/2 - text.get_width()/2, 500))
    
    return p, r_pos, h_pos, c

def tilecheck(x, y, grid, tile): #to make sure the rectangle is only rendered on the first square
    if (x == 0 or grid[y][x-1] == tile) and (y == 0 or grid[y-1][x] == tile):
        return True
    return False
    
def direction(x, y, grid, tile): # to check the direction of the rectangle
    global dir_

    if x < 5:
        if grid[y][x+1] == tile:
            dir_ = 'h'
    if y < 5:
        if grid[y+1][x] == tile:
            dir_ = 'v'

    return dir_
    
def collision(grid, board, rect, moving, vehicle_rects, red): #to check if selected rect will collide when moved
    colliding = False
    vehicle_rects.remove(rect)

    if moving == 'r':
        testpoint = (rect.x + rect.width + 1, rect.y)
        if testpoint[0] > board.x + board.width and rect != red:
            colliding = True
    if moving == 'l':
        testpoint = (rect.x - 1, rect.y)
        if testpoint[0] < board.x :
            colliding = True
    if moving == 'd':
        testpoint = (rect.x, rect.y + rect.height + 1)
        if testpoint [1] > board.y + board.height:
            colliding = True
    if moving == 'u':
        testpoint = (rect.x, rect.y - 1)
        if testpoint[1] < board.y:
            colliding = True

    
    for car in vehicle_rects:
        if car.collidepoint(testpoint):
            colliding = True

    return colliding

def animation(red, complete, velo):    
    acel = 0.6
    
    if red.x <= s_width:
        red.x += velo
        velo += acel
    elif red.x >= s_width:
        complete = True

    return red, complete, velo

restart_rect, nxt_rect, home_rect = reset(restart_rect, nxt_rect, home_rect, level)




while True:
    #screen.fill((129,203,248))#254,255,180))
    screen.blit(pygame.transform.scale(background, (background.get_width()*2, background.get_height()*2)),(0,0))
    mx, my = pygame.mouse.get_pos()
    
    if gamestart == False:
        gamestart, r_pos, h_pos, c = pregame(gamestart, r_pos, h_pos, rush, hour, c)

    #print(gamestart)

    if gamestart == True:
        screen.blit(board, (s_width/2 - board.get_width()/2, 48))
        
        level_font = pygame.font.Font('font.ttf', 50)
        level_num = level_font.render('Level: %d' %(level), True, (0,0,0))
        screen.blit(level_num, (30, 570))

        moves_font = pygame.font.Font('font.ttf', 35)
        moves_num = moves_font.render('Moves: %d' %(moves), True, (0,0,0))
        screen.blit(moves_num, (30, 570 + level_num.get_height() + 5))
        
        screen.blit(restart,(restart_rect.x,restart_rect.y))
        screen.blit(home, (home_rect.x,home_rect.y))
        y = 0
        for row in grid:
            x = 0
            for tile in row:
                if (gameend == False or tile == 'R'):
                    if tile == 'R' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = 'h'
                        if gameend == False:
                            red = Car(x, y, 'R', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = red.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        if red.rect.x <= s_width:
                            pygame.draw.rect(screen, colors['red'], red.rect)
    
                    if tile == 'l' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        lime = Car(x, y, 'l', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = lime.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['lime'], lime.rect)
        
                    if tile == 'y' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        yellow = Car(x, y, 'y', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = yellow.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['yellow'], yellow.rect)
                
                    if tile == 'B' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        blue = Car(x, y, 'B', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = blue.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['blue'], blue.rect)
                
                    if tile == 'L' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        black = Car(x, y, 'L', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = black.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['black'], black.rect)

                    if tile == 'g' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        grey = Car(x, y, 'g', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = grey.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['grey'], grey.rect)
    
                    if tile == 'P' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        purple = Car(x, y, 'P', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = purple.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['purple'], purple.rect)

                    if tile == 'r' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        brown = Car(x, y, 'r', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = brown.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['brown'], brown.rect)

                    if tile == 'G' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        green = Car(x, y, 'G', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = green.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['green'], green.rect)

                    if tile == 'b' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        sky = Car(x, y, 'b', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = sky.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['sky'], sky.rect)

                    if tile == 's' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        salmon = Car(x, y, 's', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = salmon.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, colors['salmon'], salmon.rect)
                
#trucks
                    if tile == 'o' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        Torange = Truck(x, y, 'o', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = Torange.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, Tcolors['Torange'], Torange.rect)

                    if tile == 'p' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        Tpink = Truck(x, y, 'p', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = Tpink.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, Tcolors['Tpink'], Tpink.rect)

                    if tile == 'c' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        Tcyan = Truck(x, y, 'c', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = Tcyan.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, Tcolors['Tcyan'], Tcyan.rect)

                    if tile == 'O' and (x == 0 or grid[y][x-1] != tile) and (y == 0 or grid[y-1][x] != tile):
                        dir_ = direction(x, y, grid, tile)
                        Tobi = Truck(x, y, 'O', dir_)
                        vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck = Tobi.logic(tile, vehicle_rects, coloring, selected_rect, selected_dir, selected_c, is_truck)
                        pygame.draw.rect(screen, Tcolors['Tobi'], Tobi.rect)
                x += 1
            y += 1

#endgame                       
        if grid[2][-1] == 'R':
            endtick += 1
            if endtick > 20:
                gameend = True
                selected = False
        if selected == True:
            screen.blit(pygame.transform.scale(outline, (selected_rect.width, selected_rect.height)), (selected_rect.x, selected_rect.y))

    if gameend == True and endtick > 35:
        red.rect, complete, velo = animation(red.rect, complete, velo)

    if complete == True and endtick > 120:
        nxt_rect.center = (500, 605)
    screen.blit(nxt, (nxt_rect.x,nxt_rect.y))
        
    
  
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        for car in vehicle_rects:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
               if car.collidepoint(mx,my) and gamestart == True and gameend == False:
                    if selected == False:
                        selected = True
                    elif selected == True and car == selected_rect:
                        selected = False
                        selected_rect = pygame.Rect(0,0,0,0)
                        selected_dir = ''
                        selected_c = ''
                        is_truck = False
                    selected_rect = car
               elif not car.collidepoint(mx,my) and car == selected_rect:
                   selected = False
                   selected_rect = pygame.Rect(0,0,0,0)
                   selected_dir = ''
                   selected_c = ''
                   is_truck = False
            
        if event.type == KEYDOWN and grid[2][-1] != 'R' and gamestart == True and gameend == False and selected == True:
            a = int((selected_rect.x - 126)/72)
            b = int((selected_rect.y - 72)/72)
            if selected_dir == 'h':
                if (event.key == K_RIGHT or event.key == 100):
                    moving = 'r'
                    if not collision(grid, board_rect, selected_rect, moving, vehicle_rects, red.rect):
                        selected_rect.x += 72
                        grid[b][a] = '.'
                        grid[b][a+2] = selected_c
                        if is_truck == True:
                            grid[b][a+3] == selected_c
                        moves += 1
                if (event.key == K_LEFT or event.key == 97):
                    moving = 'l'
                    if not collision(grid, board_rect, selected_rect, moving, vehicle_rects, red.rect):
                        selected_rect.x -= 72
                        if is_truck == True:
                            grid[b][a+2] = '.'
                        else:
                            grid[b][a+1] = '.'
                        grid[b][a-1] = selected_c
                        moves += 1
                            
            if selected_dir == 'v':
                if (event.key == K_DOWN or event.key == 115):
                    moving = 'd'
                    if not collision(grid, board_rect, selected_rect, moving, vehicle_rects, red.rect):
                        selected_rect.y += 72
                        grid[b][a] = '.'
                        grid[b+2][a] = selected_c
                        if is_truck == True:
                            grid[b+3][a] == selected_c
                        moves += 1
                if (event.key == K_UP or event.key == 119):
                    moving = 'u'
                    if not collision(grid, board_rect, selected_rect, moving, vehicle_rects, red.rect):
                        selected_rect.y -= 72
                        if is_truck == True:
                            grid[b+2][a] = '.'
                        else:
                            grid[b+1][a] = '.'
                        grid[b-1][a] = selected_c
                        moves += 1
                            
#restart button collision
        if restart_rect.collidepoint(mx,my) and gamestart == True:
            touching_r = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    restart_rect, nxt_rect, home_rect = reset(restart_rect, nxt_rect, home_rect, level)           
        else:
            touching_r = False

#next level button collision
        if nxt_rect.collidepoint(mx,my):
            touching_n = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    level += 1
                    restart_rect, nxt_rect, home_rect = reset(restart_rect, nxt_rect, home_rect, level)
                    complete = False
        else:
            touching_n = False

#home button collision
        if home_rect.collidepoint(mx,my):
            touching_h = True
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: 
                    gameend = False
                    gamestart = False
                    #   level = 1
                    restart_rect, nxt_rect, home_rect = reset(restart_rect, nxt_rect, home_rect, level)
                    r_pos = [0 - rush.get_width(), 100]
                    h_pos = [s_width, r_pos[1] + rush.get_height() + 60]
                    gamestart, r_pos, h_pos, c = pregame(gamestart, r_pos, h_pos, rush, hour, c) 
        else:
            touching_h = False

    
#button resizing
    if touching_n == True and gamestart == True:
        screen.blit(pygame.transform.scale(nxt, (74,74)),(nxt_rect.x - 5, nxt_rect.y - 5))
    if touching_r == True and gamestart == True:
        screen.blit(pygame.transform.scale(restart, (74, 74)),(restart_rect.x - 5,restart_rect.y - 5))
    if touching_h == True and gamestart == True:
        screen.blit(pygame.transform.scale(home, (74, 74)),(home_rect.x - 5,home_rect.y - 5))
        
    pygame.display.update()
    clock.tick(60)
