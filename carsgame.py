import pygame
import random
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TRACK_COLOR = (0, 255, 0)
CAR_COLOR = (255, 0, 0)
BG_COLOR = (255, 255, 255)
CAR_COUNT = 50
LAP_COUNT = 3

# Screen and clock setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game")
clock = pygame.time.Clock()

# Track boundaries
INNER_BOUNDARY = [
    (150, 100),
    (650, 100),
    (700, 250),
    (650, 400),
    (150, 400),
    (100, 250)
]

OUTER_BOUNDARY = [
    (50, 50),
    (750, 50),
    (800, 250),
    (750, 450),
    (50, 450),
    (0, 250)
]

# Basic car class
class Car:
    def __init__(self):
        self.image = pygame.Surface((30, 15))
        self.image.fill(CAR_COLOR)
        self.rect = self.image.get_rect()
        self.place_on_track()
        self.speed = random.randint(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.laps = 0
        self.checkpoints = 0

    def place_on_track(self):
        while True:
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = random.randint(0, SCREEN_HEIGHT)
            if self.is_inside_track(self.rect.centerx, self.rect.centery) and not self.is_on_inner_boundary(self.rect.centerx, self.rect.centery):
                break

    def update(self):
        new_x = self.rect.x + self.speed * math.cos(self.angle)
        new_y = self.rect.y + self.speed * math.sin(self.angle)

        # Check collision with boundaries
        if self.is_inside_track(new_x, new_y) and not self.is_on_inner_boundary(new_x, new_y):
            self.rect.x = new_x
            self.rect.y = new_y
        else:
            self.angle += math.pi / 2  # Turn 90 degrees
            self.checkpoints = 0  # Reset checkpoints

    def is_inside_track(self, x, y):
        return pygame.draw.polygon(screen, (0, 0, 0), OUTER_BOUNDARY).collidepoint(x, y)

    def is_on_inner_boundary(self, x, y):
        return pygame.draw.polygon(screen, (0, 0, 0), INNER_BOUNDARY).collidepoint(x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

cars = [Car() for _ in range(CAR_COUNT)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    for car in cars:
        car.update()

    # Draw
    screen.fill(BG_COLOR)
    pygame.draw.polygon(screen, TRACK_COLOR, OUTER_BOUNDARY)
    pygame.draw.polygon(screen, BG_COLOR, INNER_BOUNDARY)  # Inner track

    for car in cars:
        car.draw()

    pygame.display.flip()
    clock.tick(60)

    # Check for winners
    winners = [car for car in cars if car.laps >= LAP_COUNT]
    if winners:
        print("We have winners!")
        running = False

pygame.quit()
