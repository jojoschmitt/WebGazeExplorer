import json
import math
import os
from math import sqrt

from PyQt5 import uic

repo_root = os.path.dirname(os.path.abspath(__file__))


class SlidingWindow:
    def __init__(self, size):
        self.values = []
        self.size = size

    @property
    def is_full(self):
        return len(self.values) == self.size

    def append(self, value):
        if self.is_full:
            self.values.pop(0)
        self.values.append(value)

    def get(self, index):
        return self.values[index]

    def clear(self):
        self.values.clear()

    def set_values(self, values):
        self.values = values


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def from_attributes(cls, x, y):
        return cls(x, y)

    @classmethod
    def from_tuple(cls, tuple):
        x, y = tuple
        return cls(x, y)

    @property
    def is_negative_x(self):
        return self.x < 0

    @property
    def is_negative_y(self):
        return self.y < 0

    @property
    def is_negative_any(self):
        return self.is_negative_x or self.is_negative_y

    def normalize(self):
        def norm(v):
            if v == 0:
                return v
            elif v > 0:
                return 1
            else:
                return -1
        return Point(norm(self.x), norm(self.y))

    def swapped(self):
        return Point(self.y, self.x)

    def neighbour_top(self):
        return Point(self.x, self.y - 1)

    def neighbour_bottom(self):
        return Point(self.x, self.y + 1)

    def neighbour_left(self):
        return Point(self.x - 1, self.y)

    def neighbour_right(self):
        return Point(self.x + 1, self.y)

    def neighbour_top_right(self):
        return Point(self.x + 1, self.y - 1)

    def neighbour_bottom_right(self):
        return Point(self.x + 1, self.y + 1)

    def neighbour_bottom_left(self):
        return Point(self.x - 1, self.y + 1)

    def neighbour_top_left(self):
        return Point(self.x - 1, self.y - 1)

    def neighbours(self):
        return [self.neighbour_top(), self.neighbour_bottom(), self.neighbour_left(), self.neighbour_right()]

    def extended_neighbours(self):
        return [self.neighbour_top(), self.neighbour_bottom(), self.neighbour_left(), self.neighbour_right(), self.neighbour_top_right(), self.neighbour_bottom_right(), self.neighbour_bottom_left(), self.neighbour_top_left()]

    def neighbours_in_range(self, manhattan_distance):
        neighbours = []
        for distance in range(1, manhattan_distance+1):
            neighbours.extend(self.neighbours_at_range(distance))
        return neighbours

    def neighbours_at_range(self, manhattan_distance):
        neighbours = []
        for x in range(self.x - manhattan_distance, self.x + manhattan_distance + 1):
            for y in range(self.y - manhattan_distance, self.y + manhattan_distance + 1):
                # Calculate Manhattan distance
                current_manhattan_dist = abs(self.x - x) + abs(self.y - y)
                if current_manhattan_dist == manhattan_distance:
                    neighbours.append(Point(x, y))
        return neighbours

    def neighbours_as_tuple(self):
        return [self.neighbour_top().to_tuple(), self.neighbour_bottom().to_tuple(), self.neighbour_left().to_tuple(), self.neighbour_right().to_tuple()]

    def distance(self, other):
        return sqrt((other.x-self.x)**2+(other.y-self.y)**2)

    def manhattan_distance(self, other):
        return self.distance_x(other) + self.distance_y(other)

    def distance_x(self, other):
        return abs(self.x - other.x)

    def distance_y(self, other):
        return abs(self.y - other.y)

    def direction_radians(self, other):
        # Calculate the direction angle in radians
        direction_radians = math.atan2(other.y - self.y, other.x - self.x)
        return direction_radians

    def direction_degrees(self, other):
        """Convert radians to degrees
        0° - positive x-axis
        180° - negative x-axis
        90° - positive y-axis
        -90° - negative y-axis
        """
        direction_degrees = math.degrees(self.direction_radians(other))
        return direction_degrees

    def is_inside_rect(self, width, height):
        return 0 <= self.x < width and 0 <= self.y < height

    def is_inside(self, p1, p2):
        return self.in_between(self.x, p1.x, p2.x) and self.in_between(self.y, p1.y, p2.y)

    @staticmethod
    def in_between(v, v1, v2):
        return v1 <= v <= v2 or v2 <= v <= v1

    def to_tuple(self):
        return self.x, self.y


def normalize_value(value, min_value, max_value, min_normalized=0, max_normalized=1):
    assert min_value <= value <= max_value, f"{min_value} <= {value} <= {max_value} does not hold."
    if min_value == max_value:
        print(f"Normalizing equal values from min_value: {min_value} to max_value: {max_value} will always result in the same max_normalized value: {max_normalized}")
        return max_normalized
    # Normalize the value to the range [min_normalized, max_normalized]
    normalized_value = (value - min_value) / (max_value - min_value) * (
                max_normalized - min_normalized) + min_normalized
    return normalized_value


def norm_to_disp(normalized_point, display_size, target_origin_value=0):
    """Converts a normalized point to a point for a given display size.

    args:
        - normalized_point: the normalized point
        - display_size: holds width and height of the display area
        - target_origin_value: describes which origin value the target coordinate system has
        i.e. which value the system starts with
        i.e. 0 or 1 in most cases

    returns:
        - a point in the target coordinate system (e.g. pixel position)

    """
    def to_disp(value, max_disp_value):
        offset = target_origin_value-1
        return int(value * (max_disp_value+offset))

    return to_disp(normalized_point[0], display_size[0]), to_disp(normalized_point[1], display_size[1])


def count_files(directory):
    assert os.path.exists(directory)
    files = os.listdir(directory)
    return len(files)


def list_files(directory):
    assert os.path.exists(directory)
    return sorted(os.listdir(directory))


def load_ui(path):
    ui, _ = uic.loadUiType(path)
    return ui


def find_file_in_dir(file_name, start_dir):
    for root, dirs, files in os.walk(start_dir):
        if file_name in files:
            return os.path.abspath(os.path.join(root, file_name))
    return None


def absolute_to_repo_relative_path(abs_path):
    if abs_path.startswith(repo_root):
        return abs_path[len(repo_root + os.path.sep):]
    else:
        raise ValueError("The provided path is not within the repository root.")


def save_object_to_json_file(obj, file_path):
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    obj.__class__.to_json = to_json  # Add the to_json method to the object's class
    json_data = obj.to_json()
    with open(file_path, 'w') as file:
        file.write(json_data)


def from_json_file(cls, file_path):
    # Requires custom classes to have from_json method
    with open(file_path, 'r') as file:
        json_data = file.read()
    return cls.from_json(json_data)
