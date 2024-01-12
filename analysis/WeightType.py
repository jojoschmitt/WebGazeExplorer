from enum import Enum


class WeightType(Enum):
    CONSTANT = 0  # Everything is weighted equally
    INTENSITY = 1  # Weight by intensity
    ORDER = 2  # Weight by order, lower order means less weight
    DISTANCE = 3  # Weight by distance to next fixation
