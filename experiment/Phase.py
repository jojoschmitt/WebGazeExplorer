from enum import Enum


class Phase(Enum):
    # General phases repeating each round
    INSTRUCTION = 1
    EXPLORATION = 2
    STATEMENT = 3
    # Phases repeating each task
    T_INTRODUCTION = -1
    # Special phases only applicable for neutral task 0
    N_INITIAL = -4
    N_INITIAL_VALIDATION_INSTRUCTION = -3
    N_INITIAL_VALIDATION = -2
    N_FINAL_VALIDATION_INSTRUCTION = 4
    N_FINAL_VALIDATION = 5
    N_FINAL = 6

