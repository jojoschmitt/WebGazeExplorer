import cv2

from analysis.Extractor import Extractor
from analysis.HeatPoint import HeatPoint
from util import Point, SlidingWindow


class HeatSourceEliminationExtractor(Extractor):
    """Extracts HeatPoint objects from a heatmap image.

    The algorithm iteratively finds the hottest point in the heatmap, and extinguishes it from inside out.
    If the point is a valid source of heat, it is added as a heat_source.
    """
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
            width = heatmap.shape[1]
            height = heatmap.shape[0]
            if 0 <= x < width and 0 <= y < height:
                neighbours_on_display_area.append(neighbour)
                if heatmap[y][x] > 0:
                    hot_points += 1
        return hot_points >= int(len(neighbours_on_display_area) * VALIDITY_THRESHOLD)

    @staticmethod
    def _eliminate_heat_source(heat_source, heatmap):
        points_from_heat_sources = HeatSourceEliminationExtractor._find_affected_points_from_heat_source(heat_source, heatmap)
        HeatSourceEliminationExtractor._eliminate_points(points_from_heat_sources, heatmap)

    @staticmethod
    def _find_affected_points_from_heat_source(heat_source: HeatPoint, heatmap):
        """To find all affected points from a heat source, those that are ignited by the heat source,
        we take a quite simple approach that could further be refined:

        We start at the heat source, and visit all points on top, then on the bottom (change y coordinate of heat source).
        For every new point in y direction, we first visit all points to the right and then to the left.

        When visiting a point, it becomes an affected point if it is colder i.e. has lower intensity
        than previously visited points (towards the heat source).
        To keep track of the intensity trend, we use a sliding window to identify a heat drop over a larger range
        (sliding window size).

        We stop point visitations in a direction if the intensity trend, updated with the currently visited point,
        is not negative i.e. if the heat is not decreasing.
        """
        affected_points = [heat_source.position()]
        heatmap_width = heatmap.shape[1]
        heatmap_height = heatmap.shape[0]

        min_difference_x = heat_source.x
        max_difference_x = heatmap_width - heat_source.x
        min_difference_y = heat_source.y
        max_difference_y = heatmap_height - heat_source.y

        positive_x_values = [value for value in range(1, max_difference_x)] if heat_source.x < heatmap_width else []
        negative_x_values = [value for value in range(-min_difference_x, 0)] if heat_source.x > 0 else []
        negative_x_values.reverse()
        positive_y_values = [value for value in range(1, max_difference_y)] if heat_source.y < heatmap_height else []
        negative_y_values = [value for value in range(-min_difference_y, 0)] if heat_source.y > 0 else []
        negative_y_values.reverse()

        # The larger the window, the more of the weaker heat sources will be extinguished
        # The smaller the window, the more artifacts (false positive heat sources) remain
        sliding_window_size = 80
        sliding_window_y = SlidingWindow(sliding_window_size)
        sliding_window_y.append(heat_source)
        sliding_window_x = SlidingWindow(sliding_window_size)
        sliding_window_x.append(heat_source)

        def is_decreasing_intensity(sliding_window):
            if not sliding_window.is_full:
                return True
            else:
                return heatmap[sliding_window.get(0).y][sliding_window.get(0).x] > heatmap[sliding_window.get(-1).y][
                    sliding_window.get(-1).x]

        def visit_y(positive):
            sliding_window_y.set_values([heat_source])
            if positive:
                y_values = positive_y_values
            else:
                y_values = negative_y_values
            for y_diff in y_values:
                current_point = Point(heat_source.x, heat_source.y + y_diff)
                sliding_window_y.append(current_point)
                if is_decreasing_intensity(sliding_window_y):
                    affected_points.append(current_point)
                    visit_positive_x()
                    visit_negative_x()
                else:
                    break

        def visit_positive_y():
            visit_y(positive=True)

        def visit_negative_y():
            visit_y(positive=False)

        def visit_x(positive):
            y_anker_point = sliding_window_y.get(-1)
            sliding_window_x.set_values([y_anker_point])
            if positive:
                x_values = positive_x_values
            else:
                x_values = negative_x_values
            for x_diff in x_values:
                current_point = Point(heat_source.x + x_diff, y_anker_point.y)
                sliding_window_x.append(current_point)
                if is_decreasing_intensity(sliding_window_x):
                    affected_points.append(current_point)
                else:
                    break

        def visit_positive_x():
            visit_x(positive=True)

        def visit_negative_x():
            visit_x(positive=False)

        visit_positive_x()
        visit_negative_x()

        visit_positive_y()
        visit_negative_y()

        return affected_points

    @staticmethod
    def _eliminate_points(points, image):
        for point in points:
            image[point.y][point.x] = 0
