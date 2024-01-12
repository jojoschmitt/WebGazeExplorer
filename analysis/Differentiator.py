import os.path

from analysis.AnalysisConfiguration import AnalysisConfiguration
from analysis.extractors.BivariateSplineExtractor import BivariateSplineExtractor
from analysis.HeatPoint import HeatPoint
from analysis.Movement import write_movements_to_file, Movement
from analysis.analysis_utils import parse_fixations, parse_explorations, filter_fixations_for_exploration, \
    get_salience_considered_data_dir, get_movements_file_path, get_explorations_file_path, \
    get_difference_fixations_file_path
from config import RESOLUTION, SALIENCE_IMG_DIR
from util import Point, find_file_in_dir, normalize_value, norm_to_disp


class Differentiator:
    def __init__(self, config):
        self.config: AnalysisConfiguration = config

    def create_difference_fixations(self):
        """Creates difference fixations from the original observed fixations and the extracted fixations (heat sources)
        from the corresponding saliency map of the image for each observation.
        Clears all fixations that have a non-positive duration.
        Then writes the cleared difference fixations to a difference_fixations.csv file.
        """
        for pid in self.config.participants:
            difference_fixations = []

            salience_considered_directory = get_salience_considered_data_dir(pid)
            if not os.path.exists(salience_considered_directory):
                print(f"Salience considered participant directory not found, creating one ({salience_considered_directory})")
                os.makedirs(salience_considered_directory)

            difference_fixations_file_path = get_difference_fixations_file_path(pid)
            if os.path.exists(difference_fixations_file_path) and not self.config.general_overwrite:
                print(f"Difference fixations for participant {pid} already exist, skipping generation")
                continue

            fixations = parse_fixations(get_movements_file_path(pid))
            explorations = parse_explorations(get_explorations_file_path(pid))

            print(f"Generating difference fixations for participant {pid}")
            extractor = BivariateSplineExtractor(self.config.general_overwrite)
            for index, exploration in enumerate(explorations):
                print(f"Generating difference fixations for exploration {index+1}")
                saliency_map_name = self._get_saliency_map_name(exploration.img_name)
                saliency_map_path = find_file_in_dir(saliency_map_name, SALIENCE_IMG_DIR)

                heat_sources = extractor.get_heat_sources_from_heatmap(saliency_map_path)
                original_fixations = filter_fixations_for_exploration(exploration, fixations)

                difference_fixations.extend(self._calculate_difference_fixations_for_exploration(original_fixations, heat_sources))

            # Clear all fixations that have a non-positive duration
            cleared_difference_fixations = []
            for difference_fixation in difference_fixations:
                if difference_fixation.duration > 0:
                    cleared_difference_fixations.append(difference_fixation)

            print(f"Writing difference fixations for participant {pid} to\n\t{difference_fixations_file_path}")
            write_movements_to_file(cleared_difference_fixations, difference_fixations_file_path)

    def _calculate_difference_fixations_for_exploration(self, original_fixations: list[Movement], heat_sources: list[HeatPoint]) -> list[Movement]:
        """Convert intensity of heat sources to a scaled duration matching fixation durations.
        Subtract scaled durations from original fixation durations.
        Only original fixations that are in range of a heat source have their duration decreased.

        The maximum range of a heat source is derived from its intensity.
        The exact value of the subtracted duration depends on the scaled duration
        and the distance from the heat source to the fixation.
        The duration value decreases linearly from the center of a heat source towards its maximum range.
        """
        difference_fixations = original_fixations.copy()
        if not original_fixations:
            return difference_fixations
        max_fixation_duration = max([fixation.duration for fixation in original_fixations])
        max_heat_intensity = max([source.intensity for source in heat_sources])
        for heat_source in heat_sources:
            impact_radius = heat_source.intensity
            source_intensity_as_duration = normalize_value(heat_source.intensity, 0, max_heat_intensity, 0, max_fixation_duration)
            for fixation in difference_fixations:
                norm_point_tuple = (fixation.average_gaze_point2d_x, fixation.average_gaze_point2d_y)
                disp_point_tuple = norm_to_disp(norm_point_tuple, RESOLUTION)
                fixation_point = Point.from_tuple(disp_point_tuple)
                distance = heat_source.distance(fixation_point)
                fixation_in_range = distance <= impact_radius
                if fixation_in_range:
                    fixation.duration = fixation.duration - self._duration_at_range(distance, impact_radius, source_intensity_as_duration)
        return difference_fixations

    @staticmethod
    def _get_saliency_map_name(img_name):
        return f"{img_name.split('-')[0]}-saliency.png"

    def _duration_at_range(self, distance, max_range, max_duration):
        return max_duration - (max_duration / max_range) * distance