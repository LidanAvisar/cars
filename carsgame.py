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
CAR_COUNT = 1
LAP_COUNT = 3
LOOK_AHEAD = 10
INITIAL_CAR_SPEED = 0
CAR_REGULAR_MAX_SPEED=4
CHECKPOINT_RADIUS = 10
DISTANCE_FROM_CHECKPOINT = 60
NITRO_SPEED=3
NITRO_DURATION=2000
GAS_SPEED_INCREASE=0.005

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
CHECKPOINTS = [
    ((OUTER_BOUNDARY[1][0] + INNER_BOUNDARY[1][0]) // 2, (OUTER_BOUNDARY[1][1] + INNER_BOUNDARY[1][1]) // 2),
    ((OUTER_BOUNDARY[2][0] + INNER_BOUNDARY[2][0]) // 2, (OUTER_BOUNDARY[2][1] + INNER_BOUNDARY[2][1]) // 2),
    ((OUTER_BOUNDARY[3][0] + INNER_BOUNDARY[3][0]) // 2, (OUTER_BOUNDARY[3][1] + INNER_BOUNDARY[3][1]) // 2),
    ((OUTER_BOUNDARY[4][0] + INNER_BOUNDARY[4][0]) // 2, (OUTER_BOUNDARY[4][1] + INNER_BOUNDARY[4][1]) // 2),
    ((OUTER_BOUNDARY[5][0] + INNER_BOUNDARY[5][0]) // 2, (OUTER_BOUNDARY[5][1] + INNER_BOUNDARY[5][1]) // 2),
    ((OUTER_BOUNDARY[0][0] + INNER_BOUNDARY[0][0]) // 2, (OUTER_BOUNDARY[0][1] + INNER_BOUNDARY[0][1]) // 2),
]

spills = []

def dot_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def track_direction_at_point(x, y):
    closest_points = sorted(OUTER_BOUNDARY, key=lambda point: (point[0]-x)**2 + (point[1]-y)**2)[:2]
    dir_vector = (closest_points[1][0] - closest_points[0][0], closest_points[1][1] - closest_points[0][1])
    magnitude = math.sqrt(dir_vector[0]**2 + dir_vector[1]**2)
    return (dir_vector[0] / magnitude, dir_vector[1] / magnitude)

# Add constants
OIL_SPILL_DURATION = 2000  # 2 seconds in milliseconds
OIL_SPILL_RADIUS = 30
OIL_SPILL_COLOR = (0, 0, 0)

class Spill:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.creation_time = pygame.time.get_ticks()

    def draw(self):
        pygame.draw.circle(screen, OIL_SPILL_COLOR, (self.x, self.y), OIL_SPILL_RADIUS)

    def is_expired(self):
        return pygame.time.get_ticks() - self.creation_time > OIL_SPILL_DURATION


class Car:
    def __init__(self, name):
        self.image = pygame.image.load("car.png") 
        self.rect = self.image.get_rect()
        self.place_on_track()
        self.speed = INITIAL_CAR_SPEED
        self.angle = 0  # Start driving to the right
        self.laps = 0
        self.name = name
        self.next_checkpoint = 0  # index of the next checkpoint to cross
        self.checkpoints_crossed = 0  # how many checkpoints the car has crossed so far
        self.has_oil_spill = True
        self.on_oil_spill = False  # Is the car currently on an oil spill?
        self.nitrosLeft=4
        self.usingNitro=False
        self.nitroUsedTime=pygame.time.get_ticks()
        self.regularSpeed=INITIAL_CAR_SPEED
        
        # Cache car name text
        self.name_text = pygame.font.SysFont(None, 25).render(self.name, True, (0, 0, 0))

    def place_on_track(self):
        self.rect.x = random.randint(OUTER_BOUNDARY[0][0], INNER_BOUNDARY[0][0] - self.rect.width)
        self.rect.y = random.randint(OUTER_BOUNDARY[0][1], INNER_BOUNDARY[0][1] - self.rect.height)

    def update(self):
        chosenAction=None
        
        ROTATE_RIGHT="ROTATE_RIGHT"
        ROTATE_LEFT="ROTATE_LEFT"
        GAS="GAS"
        DROP_OIL="DROP_OIL"
        ACTIVATE_NITRO="ACTIVATE_NITRO"
            
        prev_x, prev_y = self.rect.centerx, self.rect.centery
        ahead_x = self.rect.centerx + LOOK_AHEAD * math.cos(self.angle)
        ahead_y = self.rect.centery + LOOK_AHEAD * math.sin(self.angle)

        import random

        if self.nitrosLeft>0 and not self.usingNitro and random.random() < 0.02 :
            chosenAction = ACTIVATE_NITRO
        elif  self.has_oil_spill and random.random() < 0.02:
            chosenAction = DROP_OIL
        elif not self.is_inside_track(ahead_x, ahead_y) or self.is_on_inner_boundary(ahead_x, ahead_y):
            chosenAction=ROTATE_RIGHT
        else:
            chosenAction=GAS

        print(f"{chosenAction} time {pygame.time.get_ticks()}")
        #Handle chosen action
        if chosenAction==ACTIVATE_NITRO and self.nitrosLeft>0 and not self.usingNitro:
            self.usingNitro=True
            self.nitrosLeft-=1
        elif chosenAction==DROP_OIL and self.has_oil_spill:
            spills.append(Spill(self.rect.centerx - 40* math.cos(self.angle), self.rect.centery - 40* math.sin(self.angle)))
            self.has_oil_spill = False
        elif (chosenAction==ROTATE_RIGHT):
            self.angle += math.pi / 16
        elif (chosenAction==ROTATE_LEFT): 
            self.angle -= math.pi / 16 
        elif (chosenAction==GAS):
            self.regularSpeed+=GAS_SPEED_INCREASE
            if self.regularSpeed>CAR_REGULAR_MAX_SPEED:
                self.regularSpeed=CAR_REGULAR_MAX_SPEED
            
        self.move_forward()
            
        self.handle_collisions()  # Check and handle collisions with other cars

        move_direction = (self.rect.centerx - prev_x, self.rect.centery - prev_y)
        magnitude = math.sqrt(move_direction[0]**2 + move_direction[1]**2)
        if magnitude != 0:
            move_direction = (move_direction[0] / magnitude, move_direction[1] / magnitude)
            track_dir = track_direction_at_point(self.rect.centerx, self.rect.centery)
        
        
        checkpoint_x, checkpoint_y = CHECKPOINTS[self.next_checkpoint]
        if math.sqrt((self.rect.centerx - checkpoint_x)**2 + (self.rect.centery - checkpoint_y)**2) < DISTANCE_FROM_CHECKPOINT:
            self.checkpoints_crossed += 1
            self.next_checkpoint = (self.next_checkpoint + 1) % len(CHECKPOINTS)
            #print(f"Checkpoint {self.checkpoints_crossed} finished by car {self.name}")

        #if self.checkpoints_crossed == len(CHECKPOINTS):
            #print(f"All checkpoints finished by car {self.name}")
        # Check if the car has crossed the start line
        if prev_x < INNER_BOUNDARY[0][0] and ahead_x >= INNER_BOUNDARY[0][0] and self.checkpoints_crossed == len(CHECKPOINTS):
            if not self.has_oil_spill: #Give an oil spill every lap
                self.has_oil_spill = True
            self.laps += 1
            self.checkpoints_crossed = 0
        

                        
        # Check if the car is on an oil spill
        self.on_oil_spill = False
        for spill in spills:
            distance_to_spill = math.sqrt((self.rect.centerx - spill.x)**2 + (self.rect.centery - spill.y)**2)
            if distance_to_spill <= OIL_SPILL_RADIUS:
                self.on_oil_spill = True
                break
            
        #After 2 seconds nitro should stop
        if self.usingNitro and pygame.time.get_ticks()-self.nitroUsedTime>NITRO_DURATION:
            self.usingNitro=False

        
        if self.usingNitro and not self.on_oil_spill:
            self.speed = NITRO_SPEED*self.regularSpeed
            print("Using nitro speed")
        elif self.on_oil_spill:
            self.speed = 0.2 * self.regularSpeed
        else:
            self.speed = self.regularSpeed




    def move_forward(self):
        futureX=self.rect.x + self.speed * math.cos(self.angle)
        futureY=self.rect.y + self.speed * math.sin(self.angle)
        print(f"Is current inside track ? {self.is_inside_track(self.rect.x, self.rect.y)}")
        print(f"Is current on inner boundary? {self.is_on_inner_boundary(self.rect.x, self.rect.y)}")
        print(f"current position {self.rect.x}, {self.rect.y}")
        print(f"Future position {futureX}, {futureY}")
        print(f"Is future inside track ? {self.is_inside_track(futureX, futureY)}")
        print(f"Is future on inner boundary? {self.is_on_inner_boundary(futureX, futureY)}")
        if self.is_inside_track(futureX, futureY) and not self.is_on_inner_boundary(futureX, futureY):
            self.rect.x = futureX
            self.rect.y =futureY

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
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # Creates a temporary transparent surface
        pygame.draw.polygon(temp_surface, (0, 0, 0), OUTER_BOUNDARY)
        return temp_surface.get_at((int(x), int(y))) == (0, 0, 0, 255)  # Check if the pixel at (x, y) is black

    def is_on_inner_boundary(self, x, y):
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)  # Creates a temporary transparent surface
        pygame.draw.polygon(temp_surface, (0, 0, 0), INNER_BOUNDARY)
        return temp_surface.get_at((int(x), int(y))) == (0, 0, 0, 255)  # Check if the pixel at (x, y) is black


    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)
        screen.blit(self.name_text, (self.rect.x, self.rect.y + self.rect.height))

leaderboard_cache = []

def display_leaderboard():

    sorted_cars = sorted(cars, key=lambda car: car.laps*100+car.checkpoints_crossed, reverse=True)[:5]
    y_start = 10

    for i, car in enumerate(sorted_cars):
        font = pygame.font.SysFont(None, 35)
        checkpointPercentage=round(car.checkpoints_crossed/len(CHECKPOINTS)*100)
        text = font.render(f"{i+1}. {car.name} - {car.laps} laps %{checkpointPercentage}", True, (0, 0, 0))
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
        # Draw checkpoints
    for checkpoint in CHECKPOINTS:
        pygame.draw.circle(screen, (0, 0, 255), checkpoint, CHECKPOINT_RADIUS)

    # Draw the oil spills
    for spill in spills:
        spill.draw()

    # Remove expired oil spills
    spills = [spill for spill in spills if not spill.is_expired()]
    
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
        running = False

pygame.quit()
