import pygame
import random
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 800
TRACK_COLOR = (0, 255, 0)
CAR_COLOR = (255, 0, 0)
WRONG_DIR_COLOR = CAR_COLOR
BG_COLOR = (255, 255, 255)
START_LINE_COLOR = (255, 255, 0)
CAR_COUNT = 8
LAP_COUNT = 3
LOOK_AHEAD = 50
CAR_SPEED=4

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game")
clock = pygame.time.Clock()

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

def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def track_direction_at_point(x, y):
    closest_points = sorted(OUTER_BOUNDARY, key=lambda point: (point[0]-x)**2 + (point[1]-y)**2)[:2]
    dir_vector = (closest_points[1][0] - closest_points[0][0], closest_points[1][1] - closest_points[0][1])
    magnitude = math.sqrt(dir_vector[0]**2 + dir_vector[1]**2)
    return (dir_vector[0] / magnitude, dir_vector[1] / magnitude)

class Car:
    def __init__(self, name):
        self.image = pygame.image.load("car.png")  # Replace "car.png" with the path to your car image
        self.rect = self.image.get_rect()
        self.place_on_track()
        self.speed = CAR_SPEED
        self.angle = 0  # Start driving to the right
        self.laps = 0
        self.name = name

        # Cache car name text
        self.name_text = pygame.font.SysFont(None, 25).render(self.name, True, (0, 0, 0))

    def place_on_track(self):
        self.rect.x = random.randint(OUTER_BOUNDARY[0][0], INNER_BOUNDARY[0][0] - self.rect.width)
        self.rect.y = random.randint(OUTER_BOUNDARY[0][1], INNER_BOUNDARY[0][1] - self.rect.height)

    def update(self):
        prev_x, prev_y = self.rect.centerx, self.rect.centery
        ahead_x = self.rect.centerx + LOOK_AHEAD * math.cos(self.angle)
        ahead_y = self.rect.centery + LOOK_AHEAD * math.sin(self.angle)
        
        if not self.is_inside_track(ahead_x, ahead_y) or self.is_on_inner_boundary(ahead_x, ahead_y):
            if random.choice([True, False]):
                self.angle += math.pi / 8  
            else:
                self.angle -= math.pi / 8  
        else:
            self.move_forward()

        self.handle_collisions()  # Check and handle collisions with other cars

        move_direction = (self.rect.centerx - prev_x, self.rect.centery - prev_y)
        magnitude = math.sqrt(move_direction[0]**2 + move_direction[1]**2)
        if magnitude != 0:
            move_direction = (move_direction[0] / magnitude, move_direction[1] / magnitude)
            track_dir = track_direction_at_point(self.rect.centerx, self.rect.centery)
        
            # Check if the car has crossed the start line
        if prev_x < INNER_BOUNDARY[0][0] and ahead_x >= INNER_BOUNDARY[0][0]:
            self.laps += 1  # Increment laps when crossing the start line



    def move_forward(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

    def handle_collisions(self):
        for other_car in cars:
            if other_car != self and self.rect.colliderect(other_car.rect):
                overlap_x = other_car.rect.centerx - self.rect.centerx
                overlap_y = other_car.rect.centery - self.rect.centery
                overlap_distance = math.sqrt(overlap_x**2 + overlap_y**2)

                # Calculate the unit vector of overlap direction
                if overlap_distance != 0:
                    overlap_direction = (overlap_x / overlap_distance, overlap_y / overlap_distance)
                else:
                    overlap_direction = (0, 0)

                # Move both cars away from each other based on the overlap
                move_distance = overlap_distance / 2
                self.rect.x -= overlap_direction[0] * move_distance
                self.rect.y -= overlap_direction[1] * move_distance
                other_car.rect.x += overlap_direction[0] * move_distance
                other_car.rect.y += overlap_direction[1] * move_distance

                # Adjust angles to simulate the push effect (you can fine-tune this)
                self.angle += math.pi / 8
                other_car.angle -= math.pi / 8

    def is_inside_track(self, x, y):
        return pygame.draw.polygon(screen, (0, 0, 0), OUTER_BOUNDARY).collidepoint(x, y)

    def is_on_inner_boundary(self, x, y):
        return pygame.draw.polygon(screen, (0, 0, 0), INNER_BOUNDARY).collidepoint(x, y)

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)
        screen.blit(self.name_text, (self.rect.x, self.rect.y + self.rect.height))

leaderboard_cache = []

def display_leaderboard():

    sorted_cars = sorted(cars, key=lambda car: car.laps, reverse=True)[:5]
    y_start = 10

    for i, car in enumerate(sorted_cars):
        font = pygame.font.SysFont(None, 35)
        text = font.render(f"{i+1}. {car.name} - {car.laps} laps", True, (0, 0, 0))
        y_start += 40
        screen.blit(text, (10,y_start))

car_names = [f"Car {i+1}" for i in range(CAR_COUNT)]
cars = [Car(name) for name in car_names]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for car in cars:
        car.update()

    screen.fill(BG_COLOR)
    pygame.draw.polygon(screen, TRACK_COLOR, OUTER_BOUNDARY)
    pygame.draw.polygon(screen, BG_COLOR, INNER_BOUNDARY)
    pygame.draw.line(screen, START_LINE_COLOR, OUTER_BOUNDARY[0], INNER_BOUNDARY[0], 5)

    for car in cars:
        car.draw()

    display_leaderboard()

    # Draw FPS counter
    fps_text = pygame.font.SysFont(None, 25).render(f"FPS: {int(clock.get_fps())}", True, (0, 0, 0))
    screen.blit(fps_text, (SCREEN_WIDTH - 70, 10))

    pygame.display.flip()
    clock.tick(60)

    winners = [car for car in cars if car.laps >= LAP_COUNT]
    if winners:
        print(f"Winner: {winners[0].name}")
        # running = False

pygame.quit()
