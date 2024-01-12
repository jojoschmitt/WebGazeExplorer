import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import SmoothBivariateSpline

from analysis.Extractor import Extractor
from analysis.HeatPoint import HeatPoint


class BivariateSplineExtractor(Extractor):
    """Extracts HeatPoint objects from a heatmap image.

    The algorithm fits a bivariate spline to the heatmap and finds the local maxima within the spline.
    As the local maxima represent the heat sources.
    """
    def __init__(self, overwrite=False):
        super().__init__(overwrite)

    def _extract_heat_sources_from_heatmap(self):
        heatmap_image = plt.imread(self.heatmap_path)

        heatmap_width = heatmap_image.shape[1]
        heatmap_height = heatmap_image.shape[0]

        # Subsample the data for fitting the spline
        subsample_factor = 10  # Adjust as needed
        heatmap_image_subsampled = heatmap_image[::subsample_factor, ::subsample_factor]
        x_subsampled = np.arange(0, heatmap_width, subsample_factor)
        y_subsampled = np.arange(0, heatmap_height, subsample_factor)

        # Create a grid corresponding to the image coordinates
        X, Y = np.meshgrid(x_subsampled, y_subsampled)
        # Flatten the coordinates and grayscale values for spline fitting
        x_flat = X.flatten()
        y_flat = Y.flatten()
        z_flat = heatmap_image_subsampled.flatten()

        # Fit a bivariate spline to the data
        smoothing_factor = 0.1  # Adjust as needed
        spline = SmoothBivariateSpline(y_flat, x_flat, z_flat, s=smoothing_factor)

        # Create a finer grid for the 3D surface plot
        fine_grid_resolution = 2 ** 9  # Adjust as needed (2 ** 8=256)
        x_fine = np.linspace(0, heatmap_width - 1, fine_grid_resolution)
        y_fine = np.linspace(0, heatmap_height - 1, fine_grid_resolution)
        X_fine, Y_fine = np.meshgrid(x_fine, y_fine)

        # Normalized Z values after spline fitting process.
        Z_fine = spline(y_fine, x_fine)

        # Initialize lists to store the coordinates of local maxima
        x_maxima = []
        y_maxima = []
        z_maxima = []

        # Define a neighborhood size for checking local maxima
        neighborhood_size = 5  # Adjust as needed
        for i in range(neighborhood_size, Z_fine.shape[0] - neighborhood_size):
            for j in range(neighborhood_size, Z_fine.shape[1] - neighborhood_size):
                neighborhood = Z_fine[i - neighborhood_size:i + neighborhood_size + 1,
                               j - neighborhood_size:j + neighborhood_size + 1]
                if Z_fine[i, j] == np.max(neighborhood) and int(
                        heatmap_image[int(y_fine[i])][int(x_fine[j])] * 255) > 0:
                    x_maxima.append(x_fine[j])
                    y_maxima.append(y_fine[i])
                    z_maxima.append(Z_fine[i, j])

        x_maxima = np.array(x_maxima)
        y_maxima = np.array(y_maxima)
        z_maxima = np.array(z_maxima)

        # # Create the 3D surface plot
        # matplotlib.use('Qt5Agg')
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # ax.invert_yaxis()
        # ax.plot_surface(X_fine, Y_fine, Z_fine, cmap='viridis')
        # # Mark local maxima as red points
        # ax.scatter(x_maxima, y_maxima, z_maxima, c='red', s=30, marker='o')
        # plt.show()

        for x, y in zip(x_maxima, y_maxima):
            x_max = int(x)
            y_max = int(y)
            z_max = int(heatmap_image[y_max][x_max] * 255)
            self.heat_sources.append(HeatPoint(x_max, y_max, z_max))
