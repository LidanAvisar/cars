from carsgame import Car, ACTIVATE_NITRO, DROP_OIL, GAS, ROTATE_LEFT, ROTATE_RIGHT,GameState,CarController
LOOK_AHEAD = 10
import math
import random

class CPUCarController(CarController):
    def __init__(self, car_id: str):
        self.car_id = car_id

    @property
    def id(self) -> str:
        return "cpu1"


    def decide_what_to_do_next(self, gameState: GameState) -> str:
        cars=gameState.cars
        car=cars[0]
        ahead_x = car.rect.centerx + LOOK_AHEAD * math.cos(car.angle)
        ahead_y = car.rect.centery + LOOK_AHEAD * math.sin(car.angle)

        

        if car.nitrosLeft>0 and not car.usingNitro and random.random() < 0.02 :
            chosenAction = ACTIVATE_NITRO
        elif  car.has_oil_spill and random.random() < 0.02:
            chosenAction = DROP_OIL
        elif not car.is_on_track(ahead_x, ahead_y):
            chosenAction=ROTATE_RIGHT
        else:
            chosenAction=GAS
        return chosenAction

