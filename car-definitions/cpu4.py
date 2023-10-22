from carsgame import Car, ACTIVATE_NITRO, DROP_OIL, GAS, ROTATE_LEFT, ROTATE_RIGHT,GameState,CarController,SHOOT_MISSILE
from logichelper import trivialLogic

import math
import random


LOOK_AHEAD = 50

class CPUCarController(CarController):
    def __init__(self, car_id: str):
        self.car_id = car_id
        self.previousPosition = None
    @property
    def id(self) -> str:
        return "cpu4"


    def decide_what_to_do_next(self, gameState: GameState) -> str:
        chosenAction=trivialLogic(self,gameState)
        return chosenAction

