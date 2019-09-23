import pygame
import argparse
import sys
import json
import pytuio as tuio

screenwidth = 800
screenheight = 600
fullscreen_width = 0
fullscreen_height = 0
config = json.load(open("config.json"))

def init_tuio(args):
    tracking = tuio.Tracking(args.ip,args.port)
    print("loaded profiles:", tracking.profiles.keys())
    print("list functions to access tracked objects:", tracking.get_helpers())
    return tracking


def pygame_init():
    pygame.display.init()
    global fullscreen_width
    fullscreen_width = pygame.display.Info().current_w
    global fullscreen_height
    fullscreen_height = pygame.display.Info().current_h
    
    size = screenwidth, screenheight
    screen = pygame.display.set_mode(size)
    screen = pygame.display.set_mode([fullscreen_width,fullscreen_height], flags=pygame.FULLSCREEN)
    return screen

def checkCollision(pos1, dia1, pos2, dia2):
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    # L2-norm
    return dx * dx + dy * dy < (dia1+dia2) * (dia1+dia2)

def pos2px(x,y):
    return (int(fullscreen_width *x), int(fullscreen_height*y))

def getVelocity(oldpos, newpos):
    speed = [oldpos[0] - newpos[0], oldpos[1] - newpos[1]] # delta
    norm = (speed[0]**2 + speed[1]**2)**(0.5)
    if norm == 0:
        return [0,0]
    speed[0] /= norm
    speed[1] /= norm
    return speed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert shape to geojson")
    parser.add_argument('--ip', type=str, default=config["tuio_host"],help="the IP address of the tuio host. If omitted, read from config.json")
    parser.add_argument('--port', type=int, default=int(config["tuio_port"]),help="the port of the tuio host. If omitted, read from config.json")
    parser.add_argument('--updates', type=int, default=1,help="number of TUIO updates per frame")
    args = parser.parse_args()

    # initialise
    tracking = init_tuio(args)
    screen = pygame_init()
    isFullscreen = True
    black = 0, 0, 0

    player1id = 1
    player2id = 2

    ballPos = [int(fullscreen_width/2), int(fullscreen_height/2)]
    ballSpeed = [0, 0]

    player1pos = (0,0)
    player1speed = [0,0]
    player2pos = (0, int(fullscreen_height/2) )
    player2speed = [0,0]

    player1score = 0
    player2score = 0

    playerDiameter = 70

    pygame.font.init()
    #print( pygame.font.get_fonts())
    # pick a font
    myfont = pygame.font.Font("comic.ttf", 40)

    while True:
        # handle objects
        for i in range(args.updates):
            tracking.update()

        for obj in tracking.objects():
            #print(obj.xmot,obj.ymot)
            if obj.id == player1id:
                player1speed = getVelocity(player1pos,pos2px(obj.xpos, obj.ypos))
                player1pos = pos2px(obj.xpos, obj.ypos)
                #player1speed = [obj.xmot, obj.ymot]
            if obj.id == player2id:
                player2speed = getVelocity(player2pos,pos2px(obj.xpos, obj.ypos))
                player2pos = pos2px(obj.xpos, obj.ypos)
                #player2speed = [obj.xmot, obj.ymot]

        #update ball
        ballPos[0] = int(ballPos[0] + ballSpeed[0])
        ballPos[1] = int(ballPos[1] + ballSpeed[1])

        # drawing
        screen.fill(black)
        pygame.draw.circle(screen, (255,0,0), player1pos, playerDiameter)
        #print(player1pos)
        pygame.draw.circle(screen, (0,0,255), player2pos , playerDiameter)
        pygame.draw.circle(screen, (255,255,255), ballPos , 20)
        
        # print score
        # apply it to text on a label
        label = myfont.render(str(player1score), 1, (255,0,0))
        # put the label object on the screen at right edge
        screen.blit(label, (fullscreen_width - 100, 10))
        # apply it to text on a label
        label = myfont.render(str(player2score), 1, (0,0,255))
        # put the label object on the screen at left edge
        screen.blit(label, (10, 10))
        pygame.display.flip()

        # check ball contact
        if checkCollision(player1pos,playerDiameter,ballPos,20):
            #p1 hit ball
            ballSpeed = [10* player1speed[0],10* player1speed[1]] 
            pass
        if checkCollision(player2pos,playerDiameter,ballPos,20):
            #p2 hit ball
            ballSpeed = [10* player2speed[0],10* player2speed[1]] 
            pass

        # scoring
        if ballPos[0] < 0:
            player1score += 1
            ballPos = [int(fullscreen_width/2), int(fullscreen_height/2)]
            ballSpeed = [0,0]
        if ballPos[0] > fullscreen_width:
            player2score += 1
            ballPos = [int(fullscreen_width/2), int(fullscreen_height/2)]
            ballSpeed = [0,0]

        # bouncing
        if ballPos[1] < 0:
            ballSpeed[1] *= -1
        if ballPos[1] > fullscreen_height:
            ballSpeed[1] *= -1

        # Keyboard input
        keys = []   # reset input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

        if keys != []:
            if keys[pygame.K_ESCAPE]:
                sys.exit()

            # toggle fullscreen mode
            if keys[pygame.K_SPACE]:
                if not isFullscreen:
                    screen = pygame.display.set_mode([fullscreen_width,fullscreen_height], flags=pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode([screenwidth, screenheight])
                isFullscreen = not isFullscreen

            if keys[pygame.K_RETURN]:
                ballPos = [int(fullscreen_width/2), int(fullscreen_height/2)]
                ballSpeed = [0,0]
