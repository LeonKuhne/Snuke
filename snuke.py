import pygame
import time
import random
import math
from pygame import gfxdraw

WIDTH = 1920
HEIGHT = 1080
SHOT_INTERVAL = 0.2  # in seconds
FOOD_SIZE = 20
AXIS_THRESHOLD = 0.2

class Snake:
    def __init__(self, color, start):
        self.color = color
        self.x = start[0]
        self.y = start[1]
        self.xVel = 0
        self.yVel = 0
        self.length = 20
        self.radius = 20
        self.speed = 20
        self.locHistory = []

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
        for loc in self.locHistory:
            if snake.collision(loc):
                # snake got slapped
                return True
        return False


    def feed(self):
        self.length += FOOD_SIZE

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


def draw(screen, s1, s2, food):
    screen.fill((0, 0, 0))
    s1.draw(screen)
    s2.draw(screen)

    # food
    pygame.gfxdraw.filled_circle(screen, int(food[0]), int(food[1]), 5, (255,255,0))
    pygame.gfxdraw.aacircle(screen, int(food[0]), int(food[1]), 5, (255,255,255))

    #pygame.draw.line(screen, (255,255,255), (s1.x, s1.y), (s2.x, s2.y))

    pygame.display.flip()

def joyHandle(joystick, snake):
    xTilt = joystick.get_axis(0)
    yTilt = joystick.get_axis(1)
    snake.move(xTilt, yTilt)

def start(screen, s1, s2):
    running = True
    
    food = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

    pygame.joystick.init()
    joysticks = []
    for x in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(x)
        joystick.init()
        joysticks.append(joystick)

    # start the loop
    while running:

        for event in pygame.event.get():
            # quit
            if event.type == pygame.QUIT:
                running = False

        # controls
        pressed = pygame.key.get_pressed()

        # player 1
        if pressed[pygame.K_UP]:
            s1.up()
        if pressed[pygame.K_LEFT]:
            s1.left()
        if pressed[pygame.K_RIGHT]:
            s1.right()
        if pressed[pygame.K_DOWN]:
            s1.down()

        # player 2
        if pressed[pygame.K_w]:
            s2.up()
        if pressed[pygame.K_a]:
            s2.left()
        if pressed[pygame.K_d]:
            s2.right()
        if pressed[pygame.K_s]:
            s2.down()

        # controller
        if len(joysticks) > 0:
            joyHandle(joysticks[0], s1)
        if len(joysticks) > 1:
            joyHandle(joysticks[1], s2)
        
        # food
        if s1.collision(food):
            s1.feed()
            food = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        if s2.collision(food):
            s2.feed()
            food = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

        if s1.slap(s2) and s2.slap(s1):
            print('both of you guys killed eachother')
        elif s1.slap(s2):
            print('s1 wins')
            running = False
        elif s2.slap(s1):
            print('s2 wins')
            running = False


        s1.tick()
        s2.tick()

        draw(screen, s1, s2, food)

        time.sleep(1/120)


if __name__ == '__main__':
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    while True:
        s1 = Snake((100, 255, 100), (WIDTH/5, HEIGHT/2))
        s2 = Snake((255, 100, 200), (WIDTH-WIDTH/5, HEIGHT/2))
        start(screen, s1, s2)
