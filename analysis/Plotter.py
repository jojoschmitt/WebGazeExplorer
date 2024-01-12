import math
import os.path

import matplotlib.pyplot as plt
import numpy as np

import cv2
import pandas as pd
import seaborn as sns

from analysis.AnalysisConfiguration import AnalysisConfiguration
from analysis.analysis_utils import parse_fixations, parse_explorations, filter_fixations_for_exploration, \
    get_movements_file_path, get_explorations_file_path, get_difference_fixations_file_path, find_close_dividers, \
    get_participant_analysis_plot_dir, get_salience_considered_plot_dir, get_validation_analysis_file_path
from config import RESOLUTION, ANALYSIS_PLOT_DIR, ORIGINAL_IMG_DIR, ACCUMULATED_PLOT_DIR, ACCUMULATED_SALIENCE_PLOT_DIR
from util import find_file_in_dir, normalize_value, norm_to_disp


class Plotter:
    def __init__(self, config):
        self.config: AnalysisConfiguration = config

    def plot_analysis_images(self):
        if self.config.saliency:
            self.plot_salience_considered_analysis_images()
        else:
            self.plot_salience_unconsidered_analysis_images()

    def plot_salience_considered_analysis_images(self):
        for pid in self.config.participants:

            participant_plot_dir = get_participant_analysis_plot_dir(pid)
            if not os.path.exists(participant_plot_dir):
                print(f"Creating analysis plot directory for participant {pid}")
                os.mkdir(participant_plot_dir)

            participant_salience_considered_plot_dir = get_salience_considered_plot_dir(pid)
            if not os.path.exists(participant_salience_considered_plot_dir):
                print(f"Creating salience considered plot directory for participant {pid}")
                os.mkdir(participant_salience_considered_plot_dir)

            difference_fixations_file_path = get_difference_fixations_file_path(pid)
            difference_fixations = parse_fixations(difference_fixations_file_path)
            explorations = parse_explorations(get_explorations_file_path(pid))

            print(f"Generating salience considered plots for participant {pid}")
            for index, exploration in enumerate(explorations):
                print(f"Generating salience considered plots for exploration {index+1}")
                original_img_path = find_file_in_dir(exploration.img_name, ORIGINAL_IMG_DIR)
                self._plot_fixations(
                    participant_salience_considered_plot_dir, original_img_path, exploration, difference_fixations, index)
                self._plot_scanpaths(
                    participant_salience_considered_plot_dir, original_img_path, exploration, difference_fixations, index)
                self._plot_heatmaps(
                    participant_salience_considered_plot_dir, original_img_path, exploration, difference_fixations, index)

    def plot_salience_unconsidered_analysis_images(self):
        for pid in self.config.participants:

            participant_plot_dir = os.path.join(ANALYSIS_PLOT_DIR, str(pid))
            if not os.path.exists(participant_plot_dir):
                print(f"Creating plot directory for participant {pid}")
                os.makedirs(participant_plot_dir)
            fixations = parse_fixations(get_movements_file_path(pid))
            explorations = parse_explorations(get_explorations_file_path(pid))

            print(f"Generating plots for participant {pid}")
            for index, exploration in enumerate(explorations):
                print(f"Generating plots for exploration {index+1}")
                original_img_path = find_file_in_dir(exploration.img_name, ORIGINAL_IMG_DIR)

                self._plot_fixations(participant_plot_dir, original_img_path, exploration, fixations, index)
                self._plot_scanpaths(participant_plot_dir, original_img_path, exploration, fixations, index)
                self._plot_heatmaps(participant_plot_dir, original_img_path, exploration, fixations, index)

    def plot_directed_heatmaps(self, relatable_fixations_map, directed_masks):
        """Plots a directed heatmap.
        A directed heatmap is a combination of a heatmap in the background and an arrow mask on top of it.
        In our case, the heatmap intensity represents the fixation duration. Each arrow of the mask represents
        a direction by its orientation and represents a fixation's time of occurrence by its length and thickness.
        """
        directed_heatmap_names = list(relatable_fixations_map.keys())
        assert len(directed_heatmap_names) == len(directed_masks)

        def average_vector_on_grid(grid):
            """Averages x and y coordinate for all vectors in grid.
            """
            x_mean = np.mean(grid[:, :, 0])
            y_mean = np.mean(grid[:, :, 1])

            return x_mean, y_mean

        if self.config.saliency:
            specific_plot_dir = ACCUMULATED_SALIENCE_PLOT_DIR
        else:
            specific_plot_dir = ACCUMULATED_PLOT_DIR

        for index in range(len(directed_heatmap_names)):
            accumulated_heatmap_path = os.path.join(specific_plot_dir, f"{directed_heatmap_names[index]}-intensity-based-heatmap.png")
            assert os.path.exists(accumulated_heatmap_path), f"{accumulated_heatmap_path}"
            directed_heatmap_path = os.path.join(specific_plot_dir, f"{directed_heatmap_names[index]}-directed-heatmap.png")
            if os.path.exists(directed_heatmap_path) and not self.config.directed_mask_overwrite:
                return

            print(f"Plotting directed heatmap: {directed_heatmap_path}")

            directed_mask = directed_masks[index]

            heatmap = cv2.imread(accumulated_heatmap_path)
            height, width, _ = heatmap.shape
            # Initialize a blank image for plotting vectors
            visualization = np.zeros((height, width, 3), dtype=np.uint8)

            # Find a grid size that captures all pixels without remainders
            target_grid_size = 50
            grid_width, grid_height = find_close_dividers(target_grid_size, [width, height])

            max_arrow_length = min(grid_width, grid_height) // 2
            max_arrow_thickness = 1

            strengths = np.apply_along_axis(lambda row: math.sqrt(row[0]**2 + row[1]**2), axis=2, arr=directed_mask)
            max_strength = np.max(strengths)

            for y in range(0, height, grid_height):
                for x in range(0, width, grid_width):
                    grid_end_x = x + grid_width
                    grid_end_y = y + grid_height

                    grid_center_x = x + grid_width // 2
                    grid_center_y = y + grid_height // 2
                    grid_center_point = (grid_center_x, grid_center_y)
                    vector_origin = grid_center_point

                    grid = directed_mask[y:grid_end_y, x:grid_end_x]
                    average_vector = average_vector_on_grid(grid)
                    average_vector_len = math.sqrt(average_vector[0] ** 2 + average_vector[1] ** 2)
                    if average_vector_len == 0:
                        average_unit_vector = (0, 0)
                    else:
                        average_unit_vector = (average_vector[0] / average_vector_len, average_vector[1] / average_vector_len)

                    # Strength for vector in order not to exceed grid
                    norm_str = int(normalize_value(average_vector_len, 0, max_strength, 0, max_arrow_length))
                    color_norm = plt.Normalize(vmin=0, vmax=max_arrow_length)
                    color_map = plt.get_cmap('OrRd')
                    color = color_map(color_norm(norm_str))  # Convert the RGB values to a 0-255 scale
                    r, g, b, _ = tuple(int(element*255) for element in color)
                    bgr_color = (b, g, r)
                    end_x = grid_center_point[0] + int(norm_str * average_unit_vector[0])
                    end_y = grid_center_point[1] + int(norm_str * average_unit_vector[1])

                    cv2.arrowedLine(visualization, grid_center_point, (end_x, end_y), bgr_color, max_arrow_thickness)

            alpha = 0.5
            directed_heatmap = cv2.addWeighted(heatmap, 1-alpha, visualization, alpha, 0)

            cv2.imwrite(directed_heatmap_path, directed_heatmap)

    def _plot_fixations(self, participant_plot_dir, original_img_path, exploration, fixations, index):
        fixation_img_path = os.path.join(participant_plot_dir, f"{index}-fixations.png")
        if os.path.exists(fixation_img_path) and not self.config.general_overwrite:
            return

        # Load the original image
        original_img = cv2.imread(original_img_path)
        width = original_img.shape[1]
        height = original_img.shape[0]

        filtered_fixations = filter_fixations_for_exploration(exploration, fixations)
        if filtered_fixations:
            min_fixation_duration, max_fixation_duration = self._get_min_max_fixation_duration(filtered_fixations)

            for fixation_index, fixation in enumerate(filtered_fixations):
                # Extract fixation coordinates and duration
                x, y = norm_to_disp((fixation.average_gaze_point2d_x, fixation.average_gaze_point2d_y), (width, height))
                duration = fixation.duration

                # Calculate circle radius based on fixation duration
                # You can adjust the scaling factor as needed
                max_radius = 50
                min_radius = 10
                radius = int(normalize_value(duration, min_fixation_duration, max_fixation_duration, min_radius, max_radius))

                # Draw a transparent green circle on the original image
                overlay = original_img.copy()
                cv2.circle(overlay, (x, y), radius, (0, 255, 0), -1)

                # Write the fixation number in the center
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_size = cv2.getTextSize(str(fixation_index), font, font_scale, font_thickness)[0]
                text_x = x - text_size[0] // 2
                text_y = y + text_size[1] // 2
                cv2.putText(overlay, str(fixation_index), (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness,
                            cv2.LINE_AA)

                # Combine the original image and the overlay
                alpha = 0.5  # Adjust the transparency level if needed
                cv2.addWeighted(overlay, alpha, original_img, 1 - alpha, 0, original_img)

        # Save the image with fixations
        cv2.imwrite(fixation_img_path, original_img)

    def _plot_scanpaths(self, participant_plot_dir, original_img_path, exploration, fixations, index):
        scanpath_img_path = os.path.join(participant_plot_dir, f"{index}-scanpath.png")
        if os.path.exists(scanpath_img_path) and not self.config.general_overwrite:
            return

        # Load the original image
        original_img = cv2.imread(original_img_path)
        width = original_img.shape[1]
        height = original_img.shape[0]

        filtered_fixations = filter_fixations_for_exploration(exploration, fixations)

        for fixation_index, fixation in enumerate(filtered_fixations):
            # Extract fixation coordinates and duration
            x, y = norm_to_disp((fixation.average_gaze_point2d_x, fixation.average_gaze_point2d_y), (width, height))

            # Fixed circle radius
            radius = 10

            # Set dot color using BGR format
            if fixation_index == 0:
                color = (0, 255, 0)  # Green for the first fixation
            elif fixation_index == len(filtered_fixations) - 1:
                color = (0, 0, 255)  # Red for the last fixation
            else:
                color = (255, 0, 0)  # Blue for all other fixations

            # Draw connecting lines and arrows
            if fixation_index < len(filtered_fixations) - 1:
                next_fixation = filtered_fixations[fixation_index + 1]
                next_x, next_y = norm_to_disp(
                    (next_fixation.average_gaze_point2d_x, next_fixation.average_gaze_point2d_y), (width, height))

                # Draw a white line with a thicker black border
                line_thickness = 1  # Increase thickness for better visibility
                cv2.line(original_img, (x, y), (next_x, next_y), (255, 255, 255), line_thickness*2)
                cv2.line(original_img, (x, y), (next_x, next_y), (0, 0, 0), line_thickness)

            # Draw a filled circle on the original image
            cv2.circle(original_img, (x, y), radius, color, -1)

            # Write the fixation number in the center
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            text_size = cv2.getTextSize(str(fixation_index), font, font_scale, font_thickness)[0]
            text_x = x - text_size[0] // 2
            text_y = y + text_size[1] // 2
            cv2.putText(original_img, str(fixation_index), (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness,
                        cv2.LINE_AA)

        # Save the image with the scanpath
        cv2.imwrite(scanpath_img_path, original_img)

    def _plot_heatmaps(self, participant_plot_dir, original_img_path, exploration, fixations, index):
        # Load the original image
        original_img = cv2.imread(original_img_path)

        self._plot_heatmap(participant_plot_dir, original_img, exploration, fixations, index, on_orig_img=False)
        self._plot_heatmap(participant_plot_dir, original_img, exploration, fixations, index, on_orig_img=True)

    def _plot_heatmap(self, participant_plot_dir, original_img, exploration, fixations, index, on_orig_img=True):
        if on_orig_img:
            self._plot_heatmap_with_orig_img(participant_plot_dir, original_img, index)
        else:
            self._plot_heatmap_without_orig_img(participant_plot_dir, exploration, fixations, index)

    def _plot_heatmap_without_orig_img(self, participant_plot_dir, exploration, fixations, index, plot_size=RESOLUTION):
        heatmap_img_path = os.path.join(participant_plot_dir, f"{index}-heatmap-raw.png")
        filtered_fixations = filter_fixations_for_exploration(exploration, fixations)
        x_y_intensity_list = [(filtered_fixation.average_gaze_point2d_x, filtered_fixation.average_gaze_point2d_y, filtered_fixation.duration) for filtered_fixation in filtered_fixations]
        heatmap = self._create_general_heatmap(plot_size, x_y_intensity_list)
        self._plot_general_heatmap(heatmap_img_path, heatmap)

    def _plot_heatmap_with_orig_img(self, participant_plot_dir, original_img, index):
        heatmap_img_path = os.path.join(participant_plot_dir, f"{index}-heatmap.png")
        if os.path.exists(heatmap_img_path) and not self.config.general_overwrite:
            return

        raw_heatmap_img_path = os.path.join(participant_plot_dir, f"{index}-heatmap-raw.png")
        if not os.path.exists(raw_heatmap_img_path):
            raise FileNotFoundError("To plot the heatmap on top of the original image, the raw heatmap has to exist.")

        # Load the grayscale heatmap image and the original image
        heat_img = cv2.imread(raw_heatmap_img_path, cv2.IMREAD_GRAYSCALE)

        # Resize the heatmap image to match the size of the original image
        width = original_img.shape[1]
        height = original_img.shape[0]
        heat_img = cv2.resize(heat_img, (width, height))

        # Apply a colormap to the grayscale heatmap to make it colorful
        colormap = cv2.applyColorMap(heat_img, cv2.COLORMAP_JET)

        # Normalize the heatmap to make it transparent
        alpha = 0.8  # You can adjust the transparency level here
        heatmap_with_alpha = cv2.addWeighted(original_img, alpha, colormap, 1, 0)

        # Save the result to the output image
        cv2.imwrite(heatmap_img_path, heatmap_with_alpha)

    def _get_min_max_fixation_duration(self, fixations):
        assert fixations, f"Fixations must not be empty"
        fixation_durations = [fixation.duration for fixation in fixations]
        return min(fixation_durations), max(fixation_durations)

    def create_heatmap_from_heat_points(self, heat_points, plot_size=RESOLUTION):
        x_y_intensity_list = [(heat_point.x, heat_point.y, heat_point.intensity) for heat_point in heat_points]
        heatmap = self._create_general_heatmap(plot_size, x_y_intensity_list)
        return heatmap

    def plot_accumulated_heatmap_from_heat_points(self, plot_path, heat_points, plot_size=RESOLUTION):
        heatmap = self.create_heatmap_from_heat_points(heat_points, plot_size)
        self._plot_general_heatmap(plot_path, heatmap, accumulation=True)

    def _plot_general_heatmap(self, plot_path, heatmap, accumulation=False):
        """Plots a heatmap from general heatmap values (x,y,intensity),
        if the image plot does not already exist or should be overwritten.
        Intensity values are normalized.

        args:
        - plot_path: The file path to where the plot should be saved.
        - heatmap: The heatmap as a 2D numpy array to be saved.
        """
        overwrite = self.config.accumulation_overwrite if accumulation else self.config.general_overwrite
        if os.path.exists(plot_path) and not overwrite:
            return
        cv2.imwrite(plot_path, heatmap)

    def _create_general_heatmap(self, plot_size, x_y_intensity_list):
        """Creates a heatmap from general heatmap values (x,y,intensity).
        The intensity will be normalized.

        args:
            - plot_size: A tuple of (width, height) of the plot size.
            - x_y_intensity_list: List of heatmap values (x,y,intensity). The intensity does not need to be normalized.
        """
        heatmap = np.zeros((plot_size[1], plot_size[0]), dtype=np.float32)
        if not x_y_intensity_list:
            heatmap = (heatmap * 255).astype(np.uint8)
            return heatmap
        for index, x_y_intensity in enumerate(x_y_intensity_list):
            norm_x, norm_y, intensity = x_y_intensity
            x, y = norm_to_disp(
                (norm_x, norm_y), plot_size)
            heatmap[y, x] += intensity
        # Apply a Gaussian blur to the heatmap to make it smoother
        heatmap = cv2.GaussianBlur(heatmap, (0, 0), sigmaX=45)
        # Normalize values and plot heatmap
        assert heatmap.max() != 0
        heatmap = heatmap / heatmap.max()
        heatmap = (heatmap * 255).astype(np.uint8)
        return heatmap

    def plot_accumulated_scanpath_from_heat_points(self, plot_path, heat_points):
        """Plot the accumulated scanpath on a black background.
        The scanpath order is given by the heat point intensity.

        args:
            - plot_path: The absolute path to where the new scanpath image should be saved.
            - heat_points: A list of heat points. Coordinates are given in display coordinates.
        """
        if os.path.exists(plot_path) and not self.config.accumulation_overwrite:
            return
        # Order the heat points from strongest, to weakest
        ordered_heat_points = sorted(heat_points)
        ordered_heat_points.reverse()
        img_size = RESOLUTION
        background = np.zeros((img_size[1], img_size[0], 3), dtype=np.uint8)
        for index, heat_point in enumerate(ordered_heat_points):
            point = heat_point.position().to_tuple()

            # Fixed circle radius
            radius = 10

            # Set dot color using BGR format
            if index == 0:
                color = (0, 255, 0)  # Green for the first fixation
            elif index == len(ordered_heat_points) - 1:
                color = (0, 0, 255)  # Red for the last fixation
            else:
                color = (255, 0, 0)  # Blue for all other fixations

            # Draw connecting lines and arrows
            if index < len(ordered_heat_points) - 1:
                next_point = ordered_heat_points[index + 1].position().to_tuple()

                # Draw a white line with a thicker black border
                line_thickness = 1  # Increase thickness for better visibility
                cv2.line(background, point, next_point, (255, 255, 255), line_thickness*2)

            # Draw a filled circle on the original image
            cv2.circle(background, point, radius, color, -1)

            # Write the fixation number in the center
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            text_size = cv2.getTextSize(str(index), font, font_scale, font_thickness)[0]
            text_x = point[0] - text_size[0] // 2
            text_y = point[1] + text_size[1] // 2
            cv2.putText(background, str(index), (text_x, text_y), font, font_scale, (0, 0, 0), font_thickness,
                        cv2.LINE_AA)

        # Save the image with the scanpath
        cv2.imwrite(plot_path, background)

    def plot_cross_validation_analysis_results(self, dm_correlations, hm_correlations, avg_correlations):
        data = self._prepare_cross_validation_analysis_results(dm_correlations, hm_correlations, avg_correlations)
        plt.figure(figsize=(19.20, 10.80))
        sns.boxplot(x=data['Accumulation Type'], y=data['Correlation'], hue=data['Result Type'])
        plt.show()

    def save_cross_validation_analysis_results(self, dm_correlations, hm_correlations, avg_correlations):
        data = self._prepare_cross_validation_analysis_results(dm_correlations, hm_correlations, avg_correlations)
        plt.figure(figsize=(19.20, 10.80))
        sns.boxplot(x=data['Accumulation Type'], y=data['Correlation'], hue=data['Result Type'])
        validation_analysis_file_path = get_validation_analysis_file_path(self.config.accumulation_mapping.name)
        plt.savefig(validation_analysis_file_path)

    def _prepare_cross_validation_analysis_results(self, dm_correlations, hm_correlations, avg_correlations):
        """Prepares cross validation results.

        args:
            - dm_correlations: Dict, list of directed mask correlation values mapped to accumulation mapping.
            - hm_correlations: Dict, list of heatmap correlation values mapped to accumulation mapping.
            - avg_correlations: Dict, list of average correlation values of directed mask and heatmap correlations,
            mapped to accumulation mapping.
        """
        accumulation_type = []
        result_types = []
        correlations = []
        for key, value in dm_correlations.items():
            for correlation in value:
                accumulation_type.append(key)
                result_types.append("Directed Mask")
                correlations.append(correlation)
        for key, value in hm_correlations.items():
            for correlation in value:
                accumulation_type.append(key)
                result_types.append("Heatmap")
                correlations.append(correlation)
        for key, value in avg_correlations.items():
            for correlation in value:
                accumulation_type.append(key)
                result_types.append("Average")
                correlations.append(correlation)
        data = {
            'Accumulation Type': accumulation_type,
            'Result Type': result_types,
            'Correlation': correlations
        }
        data = pd.DataFrame(data)

        return data
