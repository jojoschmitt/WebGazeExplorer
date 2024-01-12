from util import Point


class HeatPoint(Point):
    def __init__(self, x, y, intensity):
        super().__init__(x, y)
        self.intensity = intensity

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.intensity == other.intensity

    def __lt__(self, other):
        return self.intensity < other.intensity

    def __hash__(self):
        return hash((self.x, self.y, self.intensity))

    @classmethod
    def from_attributes(cls, x, y, intensity):
        return cls(x, y, intensity)

    @classmethod
    def from_tuple(cls, tuple):
        x, y, intensity = tuple
        return cls(x, y, intensity)

    @classmethod
    def from_point(cls, point, intensity):
        return cls(point.x, point.y, intensity)

    def position(self):
        return Point(self.x, self.y)

    def position_as_tuple(self):
        return self.x, self.y

    def to_tuple(self):
        return self.x, self.y, self.intensity


HEAT_POINTS_FILE_HEADER = "X,Y,Intensity"


def heat_points_from_file(file_path):
    heat_points = []
    with open(file_path, 'r') as file:
        file.readline()  # Read off header line
        for line in file:
            x, y, intensity = [int(value) for value in line.strip().split(",")]
            heat_points.append(HeatPoint(x, y, intensity))
    return heat_points


def heat_points_to_file(heat_points, file_path):
    print(f"Saving heat points to file {file_path}")
    with open(file_path, 'w') as file:
        file.write(HEAT_POINTS_FILE_HEADER+"\n")
        heat_points = sorted(heat_points)
        for heat_point in heat_points:
            line = f"{heat_point.x},{heat_point.y},{heat_point.intensity}\n"
            file.write(line)
