from enum import Enum
from threading import Thread
from typing import Optional

import cv2
import numpy
import numpy as np

from analysis.Extractor import Extractor
from analysis.HeatPoint import HeatPoint
from util import Point


class AxisDirection(Enum):
    """The axis directions from the center point.
    We defined PY to be the axis on top of the center point and NY to be the axis on bottom of the center point.
    The directions for PY (0, -1) and NY (0, 1) may seem counterintuitive but are consistent with our previous
    definitions and thus correct in the context of image processing.
    """
    PY = (0, -1)
    PX = (1, 0)
    NY = (0, 1)
    NX = (-1, 0)


class Area:
    def __init__(self, array, global_origin):
        self.array: numpy.ndarray = array
        self.global_origin: tuple = global_origin
        self.dimensions = len(self.array.shape)

    def mark(self, global_point: tuple, value):
        local_point = (global_point[0] - self.global_origin[0], global_point[1] - self.global_origin[1])
        local_x = local_point[0]
        local_y = local_point[1]
        if self.dimensions == 2:
            self.array[local_y, local_x] += value
        elif self.dimensions == 1:
            # Either the x or y value will always be zero after translation and the other value will hold the index
            axis_index = max(local_x, local_y)
            self.array[axis_index] += value
        else:
            raise ValueError(f"Unsupported dimension ({self.dimensions}) for area")


class MarkerMask:
    """A mask over a rectangle.
    The mask marks points on the rectangle with values in the range of [-2, 2].
    Each point in the mask is initialized with 0 and can be increased or decreased by 1 when a point is visited.
    Each point is visited a maximum of 2 times, horizontally and vertically.
    The value is increased when visiting the point supports elimination.
    The value is decreased when visiting the point denies elimination.
    When the elimination is denied at least once, the elimination is denied entirely.

    The mask is seperated into 8 areas which split into 4 quadrants and 4 axes.

    A center point divides the rectangle into 4 quadrants. Making it effectively concurrently processable by 4 threads.

    The following abbreviations are used:
     - p: positive
     - n: negative
     - x: x-coordinates
     - y: y-coordinates

    The 4 quadrants are py-nx (top left), py-px (top right), ny-px (bottom right), ny-nx (bottom left).
    The quadrants are relative to the center point.
    Quadrants do not cover the center point's x and y axes because quadrants would otherwise overlap at these axes.

    In addition to the quadrants, there are 4 center axes that cover the center point's x and y axes but do not
    include the center point itself because they would otherwise overlap in the center point.
    The 4 center axes are py (top), px (right), ny (bottom), nx (left) all relative to the center point.
    """
    def __init__(self, center_point, width, height):
        assert center_point.is_inside_rect(width, height)
        self.center_point: Point = center_point
        self.width: int = width
        self.height: int = height

        self.py_len, self.px_len, self.ny_len, self.nx_len = self._initialize_lengths()
        self.py_nx, self.py_px, self.ny_px, self.ny_nx = self._initialize_quadrants()
        self.py, self.px, self.ny, self.nx = self._initialize_axes()

    def get_full_mask(self):
        upper_mask = np.hstack((self.py_nx.array, self.py.array.reshape(-1, 1), self.py_px.array))
        lower_mask = np.hstack((self.ny_nx.array, self.ny.array.reshape(-1, 1), self.ny_px.array))
        middle_mask = np.append(np.append(self.nx.array, 1), self.px.array)
        full_mask = np.vstack((upper_mask, lower_mask, middle_mask))
        return full_mask

    def _initialize_lengths(self):
        py_len = self.center_point.y
        px_len = self.width - (self.center_point.x + 1)
        ny_len = self.height - (self.center_point.y + 1)
        nx_len = self.center_point.x
        return py_len, px_len, ny_len, nx_len

    def _initialize_quadrants(self) -> tuple[Area, Area, Area, Area]:
        py_nx_array = np.zeros((self.py_len, self.nx_len))
        py_px_array = np.zeros((self.py_len, self.px_len))
        ny_px_array = np.zeros((self.ny_len, self.px_len))
        ny_nx_array = np.zeros((self.ny_len, self.nx_len))

        # Origin and destination points of full width and height coordinates that span quadrants
        py_nx_origin = (0, 0)
        py_px_origin = (self.center_point.x + 1, 0)
        ny_px_origin = (self.center_point.x + 1, self.center_point.y + 1)
        ny_nx_origin = (0, self.center_point.y + 1)

        py_nx = Area(py_nx_array, py_nx_origin)
        py_px = Area(py_px_array, py_px_origin)
        ny_px = Area(ny_px_array, ny_px_origin)
        ny_nx = Area(ny_nx_array, ny_nx_origin)

        return py_nx, py_px, ny_px, ny_nx

    def _initialize_axes(self) -> tuple[Area, Area, Area, Area]:
        py_array = np.zeros(self.py_len)
        px_array = np.zeros(self.px_len)
        ny_array = np.zeros(self.ny_len)
        nx_array = np.zeros(self.nx_len)

        # Origin and destination points of full width and height coordinates that span axes
        py_origin = (self.center_point.x, 0)
        px_origin = (self.center_point.x + 1, self.center_point.y)
        ny_origin = (self.center_point.x, self.center_point.y + 1)
        nx_origin = (0, self.center_point.y)

        py = Area(py_array, py_origin)
        px = Area(px_array, px_origin)
        ny = Area(ny_array, ny_origin)
        nx = Area(nx_array, nx_origin)

        return py, px, ny, nx


class HeatPointVisitor(Thread):
    def __init__(self, heatmap, marker_mask, axis_direction, relevant_points_on_primary_axis=None, relevant_points_on_support_axis=None):
        self.heatmap = heatmap
        self.heatmap_height, self.heatmap_width = self.heatmap.shape
        self.marker_mask: MarkerMask = marker_mask
        # We are using tuple for heat points here because it is more efficient to work with them.
        # We are marking about 8.000.000 points when there are 15 heat points to extract.
        self.relevant_points_on_primary_axis: list[tuple] = relevant_points_on_primary_axis
        self.relevant_points_on_support_axis: list[tuple] = relevant_points_on_support_axis
        self.primary_axis_direction: AxisDirection = axis_direction
        self.support_axis_direction: AxisDirection = None

        self.primary_axis: Optional[Area] = None
        self.support_axis: Optional[Area] = None
        self.quadrant: Optional[Area] = None
        self._init_axis_and_quadrant_info()

        super().__init__()

    def run(self) -> None:
        if not self.relevant_points_on_primary_axis:
            self._visit_axis()
        else:
            self._visit_quadrant()

    def _visit_axis(self):
        center_point = self.marker_mask.center_point.to_tuple()
        center_x = center_point[0]
        center_y = center_point[1]
        heat_source = (center_x, center_y, self.heatmap[center_y, center_x])
        visited_heat_points = [heat_source]
        axis_direction = self.primary_axis_direction.value
        self._visit_points_in_direction(visited_heat_points, axis_direction, self.primary_axis)
        self.relevant_points_on_primary_axis.extend(visited_heat_points[1:])

    def _visit_quadrant(self):
        # Visit quadrant from primary axis
        axis_direction = self.primary_axis_direction.value
        direction = (-axis_direction[1], axis_direction[0])
        self._visit_quadrant_from_axis(direction, self.relevant_points_on_primary_axis)

        # Visit quadrant from support axis
        axis_direction = self.support_axis_direction.value
        direction = (axis_direction[1], -axis_direction[0])
        self._visit_quadrant_from_axis(direction, self.relevant_points_on_support_axis)

    def _visit_quadrant_from_axis(self, direction, relevant_points_on_axis):
        for relevant_point_on_axis in relevant_points_on_axis:
            visited_heat_points = [relevant_point_on_axis]
            self._visit_points_in_direction(visited_heat_points, direction, self.quadrant)

    def _visit_points_in_direction(self, visited_heat_points, direction, area):
        while self._visit_next_point(visited_heat_points, direction, area):
            pass

    def _visit_next_point(self, visited_heat_points: list[tuple], direction: tuple, area: Area):
        """From the last visited heat point, will visit the next heat point in the given direction.

        args:
            - visited_heat_points: A list of heat points as tuples visited so far. Must not be empty.
            - direction: The direction given as a vector like tuple.
            - area: A reference to an Area object that holds the mask of the currently visited axis or quadrant.

        returns:
            - The visited_heat_points list with the point that has just been visited if the heat points show a
            negative trend i.e. are of decreasing intensity.
            - None otherwise.
        """
        # assert len(visited_heat_points) > 0
        last_point = visited_heat_points[-1]
        next_point = (last_point[0] + direction[0], last_point[1] + direction[1])
        next_x = next_point[0]
        next_y = next_point[1]

        next_point_inside_heatmap = 0 <= next_x < self.heatmap_width and 0 <= next_y < self.heatmap_height
        if not next_point_inside_heatmap:
            return False

        next_heat_point = (next_x, next_y, self.heatmap[next_y, next_x])
        visited_heat_points.append(next_heat_point)

        if self._is_negative_trend(visited_heat_points):
            # Points that should be eliminated are marked with 1
            area.mark(next_point, 1)
            return True
        else:
            # Points that seem not to be affected by the current heat source are marked with -1
            area.mark(next_point, -1)
            return False

    @staticmethod
    def _is_negative_trend(visited_heat_points: list[tuple]):
        size = 80
        if len(visited_heat_points) < size:
            return True
        else:
            # Intensity of 80th last point is higher than intensity of current point
            return visited_heat_points[-size][2] > visited_heat_points[-1][2]

    def _init_axis_and_quadrant_info(self):
        match self.primary_axis_direction:
            case AxisDirection.PY:
                self.primary_axis = self.marker_mask.py
                self.support_axis = self.marker_mask.px
                self.quadrant = self.marker_mask.py_px
                self.support_axis_direction = AxisDirection.PX
            case AxisDirection.PX:
                self.primary_axis = self.marker_mask.px
                self.support_axis = self.marker_mask.ny
                self.quadrant = self.marker_mask.ny_px
                self.support_axis_direction = AxisDirection.NY
            case AxisDirection.NY:
                self.primary_axis = self.marker_mask.ny
                self.support_axis = self.marker_mask.nx
                self.quadrant = self.marker_mask.ny_nx
                self.support_axis_direction = AxisDirection.NX
            case AxisDirection.NX:
                self.primary_axis = self.marker_mask.nx
                self.support_axis = self.marker_mask.py
                self.quadrant = self.marker_mask.py_nx
                self.support_axis_direction = AxisDirection.PY
            case _:
                raise ValueError(f"This axis direction does not exist {self.primary_axis_direction}")


class ConcurrentHeatSourceEliminationExtractor(Extractor):
    def __init__(self, overwrite):
        super().__init__(overwrite)

    def _extract_heat_sources_from_heatmap(self):
        heatmap = cv2.imread(self.heatmap_path, cv2.IMREAD_GRAYSCALE)
        saved_heatmap = heatmap.copy()
        while True:
            _, max_val, _, max_pos = cv2.minMaxLoc(heatmap)
            all_heat_sources_found = max_val == 0
            if all_heat_sources_found:
                break
            heat_source = HeatPoint(max_pos[0], max_pos[1], int(max_val))
            if self._is_valid_heat_source(heat_source, heatmap):
                self.heat_sources.append(heat_source)
            self._eliminate_heat_source(heat_source, heatmap)

    @staticmethod
    def _is_valid_heat_source(heat_point, heatmap):
        """A heat source is a valid if it spreads heat.
        To determine if the point spreads heat, we consider all surrounding points in the range
        of a fixed manhattan distance. For all points that are on the display area, we define a percentage
        threshold, of how many of these surrounding points on the display area need to be hot (non-black).
        """
        # How many neighbours need to be hot for the current point to be a heat center point (0.5 == 50%)
        VALIDITY_THRESHOLD = 0.6
        hot_points = 0
        neighbours_on_display_area = []
        for neighbour in heat_point.neighbours_in_range(2):
            x = neighbour.x
            y = neighbour.y
            height, width = heatmap.shape
            if 0 <= x < width and 0 <= y < height:
                neighbours_on_display_area.append(neighbour)
                if heatmap[y][x] > 0:
                    hot_points += 1
        return hot_points >= int(len(neighbours_on_display_area) * VALIDITY_THRESHOLD)

    def _eliminate_heat_source(self, heat_source, heatmap):
        marker_mask = self._find_affected_points_from_heat_source(heat_source, heatmap)
        self._eliminate_points(marker_mask, heatmap)

    @staticmethod
    def _eliminate_points(marker_mask, heatmap):
        assert marker_mask.shape == heatmap.shape
        heatmap[marker_mask > 0] = 0

    @staticmethod
    def _find_affected_points_from_heat_source(heat_source: HeatPoint, heatmap):
        """To find all affected points from a heat source, those that are ignited by the heat source,
        we first assign each of the 4 threads 4 axes and 4 quadrants to work on.

        The threads will first visit their axes. This on one hand fills the mask with all the values for the axes
        and on the other hand provides information about all relevant points on each axis. Basically all points
        that are affected by the heat source.

        Afterward, the threads will each work on their assigned quadrant and visit points from the direction of
        the two axes that span their quadrant.

        In the end, the areas are combined to one big mask that indicates all heat point that should be eliminated
        in the original heat map.
        """
        heatmap_height, heatmap_width = heatmap.shape
        marker_mask = MarkerMask(heat_source.position(), heatmap_width, heatmap_height)

        relevant_points_on_py_axis = []
        relevant_points_on_px_axis = []
        relevant_points_on_ny_axis = []
        relevant_points_on_nx_axis = []

        hpv_0 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.PY, relevant_points_on_py_axis, relevant_points_on_px_axis)
        hpv_1 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.PX, relevant_points_on_px_axis, relevant_points_on_ny_axis)
        hpv_2 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.NY, relevant_points_on_ny_axis, relevant_points_on_nx_axis)
        hpv_3 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.NX, relevant_points_on_nx_axis, relevant_points_on_py_axis)
        visitors = [hpv_0, hpv_1, hpv_2, hpv_3]

        # Mark axis
        for visitor in visitors:
            visitor.start()
        for visitor in visitors:
            visitor.join()

        hpv_0 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.PY, relevant_points_on_py_axis, relevant_points_on_px_axis)
        hpv_1 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.PX, relevant_points_on_px_axis, relevant_points_on_ny_axis)
        hpv_2 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.NY, relevant_points_on_ny_axis, relevant_points_on_nx_axis)
        hpv_3 = HeatPointVisitor(heatmap, marker_mask, AxisDirection.NX, relevant_points_on_nx_axis, relevant_points_on_py_axis)
        visitors = [hpv_0, hpv_1, hpv_2, hpv_3]

        # Mark quadrants
        for visitor in visitors:
            visitor.start()
        for visitor in visitors:
            visitor.join()

        return marker_mask.get_full_mask()
