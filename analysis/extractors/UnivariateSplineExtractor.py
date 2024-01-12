import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline

from analysis.Extractor import Extractor
from analysis.HeatPoint import HeatPoint
from util import Point


class UnivariateSplineExtractor(Extractor):
    def __init__(self, overwrite=False):
        super().__init__(overwrite)

    def _extract_heat_sources_from_heatmap(self):
        """Extracts HeatPoint objects from a heatmap image.

        The algorithm goes through every row and column in the heatmap and evaluates the corresponding spline.
        For each spline we calculate the local maxima and save local maxima for rows
        separately from local maxima for columns.
        The overlapping local maxima from row and column are heat sources which are returned.
        """
        heatmap = cv2.imread(self.heatmap_path, cv2.IMREAD_GRAYSCALE)

        row_maxima = []
        column_maxima = []
        assert len(heatmap) > 0
        row_len = len(heatmap[0])
        column_len = len(heatmap)
        for index, row in enumerate(heatmap):
            row_x = np.array([i for i in range(row_len)])
            row_y = row
            local_maxima = self._get_local_maxima_by_univariate_spline(row_x, row_y)
            for local_maximum in local_maxima:
                x = int(local_maximum.x)
                y = index
                intensity = heatmap[y, x]
                row_maxima.append(HeatPoint(x, y, intensity))
        for index in range(row_len):
            column = heatmap[:, index]
            column_x = np.array([i for i in range(column_len)])
            column_y = column
            local_maxima = self._get_local_maxima_by_univariate_spline(column_x, column_y)
            for local_maximum in local_maxima:
                x = index
                y = int(local_maximum.x)
                intensity = heatmap[y, x]
                column_maxima.append(HeatPoint(x, y, intensity))

        for row_maximum in row_maxima:
            if row_maximum.intensity == 0:
                continue
            for column_maximum in column_maxima:
                if row_maximum.distance(column_maximum) < 2:
                    self._update_heat_point_list(row_maximum)

    def _update_heat_point_list(self, new_heat_point):
        """Adds a new heat point to the list in case the list does not contain any heat points close to the new point.
        Replaces an existing heat point if the new heat point is hotter and close by.
        Discards the new heat point if it is close to an already existing heat point but not hotter.
        """
        for heat_point in self.heat_sources:
            if new_heat_point.distance(heat_point) < 10:
                if new_heat_point.intensity > heat_point.intensity:
                    self.heat_sources.remove(heat_point)
                    self.heat_sources.append(new_heat_point)
                return
        self.heat_sources.append(new_heat_point)

    @staticmethod
    def _get_local_maxima_by_univariate_spline(x_values, y_values) -> list[Point]:
        """Takes discrete x and y values and fits a univariate spline to find the local maxima.

        args:
        - x_values: x values in a list
        - y_values: y values in a list (maximum is identified by the y values)

        returns:
        - a list of local maxima points
        """
        # Fit a spline to the data
        smoothing_factor = 200  # Adjust as needed
        spline = UnivariateSpline(x_values, y_values, s=smoothing_factor)

        # Evaluate the spline over a finer x range
        fine_grid_resolution = 2 ** 11  # Adjust as needed (2**8=256)
        x_finer = np.linspace(min(x_values), max(x_values), fine_grid_resolution)

        # Calculate the first and second derivatives of the spline
        y_prime = spline.derivative(n=1)(x_finer)
        y_double_prime = spline.derivative(n=2)(x_finer)

        # Find the local maxima
        local_maxima_x = x_finer[:-2][(y_prime[1:-1] > 0) & (y_prime[2:] < 0) & (y_double_prime[1:-1] < 0)]
        local_maxima_y = spline(local_maxima_x)

        local_maxima = [Point(local_maxima_x[i], local_maxima_y[i]) for i in range(len(local_maxima_x))]
        return local_maxima
