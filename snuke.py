import pygame
import time
import random
import math
from pygame import gfxdraw

WIDTH = 1920
HEIGHT = 1080
SHOT_INTERVAL = 0.2  # in seconds
FOOD_SIZE = 10
AXIS_THRESHOLD = 0.2

# temp point system
scores = [0, 0]

class Snake:
    counter = 0
    
    def __init__(self, color, start, joystick, name = 'default'):
        self.id = Snake.counter
        Snake.counter += 1
        self.color = color
        self.name = name
        self.x = start[0]
        self.y = start[1]
        self.xVel = 0
        self.yVel = 0
        self.length = 20
        self.radius = 20
        self.speed = 20
        self.locHistory = []
        self.dead = False
        self.joystick = joystick
        self.score = 0
    
    def win(self):
        self.score += 1

    def move(self, xDir, yDir):
        if(abs(xDir) > AXIS_THRESHOLD):
            self.xVel += xDir
        if(abs(yDir) > AXIS_THRESHOLD):
            self.yVel += yDir
    
    def left(self):
        self.x -= self.speed
        self.xVel = -1*self.speed
        
    def right(self):
        self.x += self.speed
        self.xVel = self.speed

    def down(self):
        self.y += self.speed
        self.yVel = self.speed

    def up(self):
        self.y -= self.speed
        self.yVel = -1*self.speed

    def collision(self, food):
        if food[0] > self.x - self.radius and food[0] < self.x + self.radius:
            if food[1] > self.y - self.radius and food[1] < self.y + self.radius:
                return True
        return False

    def slap(self, snake):
        if self.id != snake.id:
            for loc in self.locHistory:
                if snake.collision(loc):
                    # snake got slapped
                    return True
        return False


    def feed(self):
        self.length += FOOD_SIZE

    def kill(self):
        self.dead = True

    def draw(self, screen):
        self.locHistory.append((self.x, self.y))
        if len(self.locHistory) > self.length:
            self.locHistory.pop(0)

        for loc in self.locHistory:
            pygame.gfxdraw.filled_circle(screen, int(loc[0]), int(loc[1]), self.radius, self.color)
            pygame.gfxdraw.aacircle(screen, int(loc[0]), int(loc[1]), self.radius, self.color)
        pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), self.radius+1, (0,0,0))
        pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), self.radius+1, self.color)

    def tick(self):
        if self.dead:
            return

        # slide
        self.xVel = self.xVel * 0.95
        self.yVel = self.yVel * 0.95
        if abs(self.xVel) < 0.01:
            self.xVel = 0
        if abs(self.yVel) < 0.01:
            self.yVel = 0
        
        totalSpeed = abs(self.xVel) + abs(self.yVel)
        if totalSpeed > self.speed:
            xRel = (self.xVel/totalSpeed) * self.speed
            yRel = (self.yVel/totalSpeed) * self.speed
            self.xVel = xRel
            self.yVel = yRel
 
        # move
        self.x += self.xVel
        self.y += self.yVel

        # sides
        if self.x > WIDTH:
            self.x = WIDTH
        elif self.x < 0:
            self.x = 0
        elif self.y > HEIGHT:
            self.y = HEIGHT
        elif self.y < 0:
            self.y = 0


def draw(screen, snakes, food):
    screen.fill((0, 0, 0))
    for snake in snakes:
        snake.draw(screen)

    # food
    pygame.gfxdraw.filled_circle(screen, int(food[0]), int(food[1]), 5, (255,255,0))
    pygame.gfxdraw.aacircle(screen, int(food[0]), int(food[1]), 5, (255,255,255))

    pygame.display.flip()

def joyHandle(snake):
    xTilt = snake.joystick.get_axis(0)
    yTilt = snake.joystick.get_axis(1)
    snake.move(xTilt, yTilt)

def start(screen, snakes):
    running = True
    
    food = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

    # start the loop
    while running:

        for event in pygame.event.get():
            # quit
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return False

        # controls
        pressed = pygame.key.get_pressed()

        # controller
        for snake in snakes:
            joyHandle(snake)
        
        # food
        for snake in snakes:
            if snake.collision(food):
                snake.feed()
                food = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

        # kill
        snakesToKill = []
        for snake in snakes:
            for slapped in snakes:
                if snake.slap(slapped):
                    if not slapped.slap(snake):
                        slapped.kill()
                        print('snake died')

        # win condition
        alive = []
        for snake in snakes:
            if not snake.dead:
                alive.append(snake)
        
        if len(alive) == 1:
            name = alive[0].name 
            if name == "Lexi":
                scores[0] += 1
            elif name == "Leon":
                scores[1] += 1
            
            print(name + ' won, scores: lexi[' + str(scores[0]) + '] leon[' + str(scores[1]) + '] ')
            
            running = False
            return True
        
        # tick
        for snake in snakes:
            snake.tick()
        
        # draw
        draw(screen, snakes, food)

        time.sleep(1/120)


'''
#
# Game Stages
#
'''

def game(screen, joysticks):
    green = (100, 255, 100)
    purple = (255, 100, 200)
    red = (255, 100, 100)
    blue = (100, 100, 255)
    colors = [green, purple, red, blue]
    playing = True

    while playing:
        snakes = []
        
        currPlayer = 0
        for joystick in joysticks:
            x = (currPlayer+1) * WIDTH//(len(joysticks)+1)
            y = HEIGHT//2
            color = colors[currPlayer]
            snake = Snake(color, (x,y), joystick)
            snakes.append(snake)
            
            currPlayer += 1
        
        print('starting round...')
        snakes[0].name = "Lexi"
        snakes[1].name = "Leon"
        playing = start(screen, snakes)

def connect(screen):
    waiting = True
    font = pygame.font.SysFont('freemono', 24)
    
    white = (255,255,255)
    black = (0,0,0)

    joysticks = []
    activeJoysticks = []
    
    while waiting:
        # create text string
        textStr = "Controller Count:" + str(pygame.joystick.get_count())
        text = font.render(textStr, True, white)
        textRect = text.get_rect()
        textRect.center = (WIDTH//2, HEIGHT//2)
    
        # input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting == False


        for joystick in joysticks:
            aButton = joystick.get_button(0)
            if aButton:
                waiting = False

        # connect joysticks
        pygame.joystick.init()
        for x in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(x)
            if x not in activeJoysticks:
                activeJoysticks.append(x)
                print('found joystick')
                joystick.init()
                joysticks.append(joystick)

        # draw
        screen.fill(black)
        screen.blit(text, textRect)
        pygame.display.flip()

        time.sleep(1/30)
    
    return joysticks


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('snuke')

    joysticks = connect(screen)
    game(screen, joysticks)
   
