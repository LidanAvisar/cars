from carsgame import Car, ACTIVATE_NITRO, DROP_OIL, GAS, ROTATE_LEFT, ROTATE_RIGHT,GameState,CarController

import math
import random


LOOK_AHEAD = 40

class CPUCarController(CarController):
    def __init__(self, car_id: str):
        self.car_id = car_id
        self.previousPosition = None
    @property
    def id(self) -> str:
        return "cpu6"


    def decide_what_to_do_next(self, gameState: GameState) -> str:
        
        my_car = next(car for car in gameState.cars if car.name == self.id)

        self.previousPosition = my_car.rect.center
        
        ahead_x = my_car.rect.centerx + LOOK_AHEAD * math.cos(my_car.angle)
        ahead_y = my_car.rect.centery + LOOK_AHEAD * math.sin(my_car.angle)

        

        if my_car.nitrosLeft>0 and not my_car.usingNitro and random.random() < 0.02 :
            chosenAction = ACTIVATE_NITRO
        elif  my_car.has_oil_spill and random.random() < 0.02:
            chosenAction = DROP_OIL
        elif not my_car.is_on_track(ahead_x, ahead_y):
            chosenAction=ROTATE_RIGHT
        elif random.random() < 0.002:
            chosenAction=ROTATE_LEFT
        else:
            chosenAction=GAS
        return chosenAction

