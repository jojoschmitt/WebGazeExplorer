import os
import statistics

import numpy as np
from scipy.stats import pearsonr

from analysis.Accumulator import Accumulator
from analysis.AnalysisConfiguration import AnalysisConfiguration
from analysis.Plotter import Plotter
from analysis.ValidationResult import ValidationResult, DirectedMaskScore, HeatMapScore, ValidationScore
from analysis.WeightType import WeightType
from analysis.analysis_utils import get_directed_mask_file_path
from config import ACCUMULATED_DIRECTED_MASK_DIR, VALIDATION_RESULT_FILE_PATH


class Validator:

    def __init__(self, config, accumulator, plotter):
        self.config: AnalysisConfiguration = config
        self.accumulator: Accumulator = accumulator
        self.plotter: Plotter = plotter
        self.file_path: str = VALIDATION_RESULT_FILE_PATH

    def leave_one_out_cross_validation(self, relatable_fixations_map):
        """Performs leave-one-out cross-validation for directed masks and heatmaps.
        Writes the correlations between left out explorations and minor accumulated explorations to files.
        """
        print(f"Starting leave-one-out cross-validation")
        for list_id, relatable_fixations_list in relatable_fixations_map.items():
            print(f"Calculating validation results for {list_id}")
            self._loucv_directed_masks(list_id, relatable_fixations_list)
            self._loucv_heatmaps(list_id, relatable_fixations_list)

    def _loucv_directed_masks(self, list_id, relatable_fixations_list):
        """Performs leave-one-out cross-validation for directed masks.
        1. Gets accumulated directed mask based on accumulation mapping
        2. Excludes one directed mask from the relatable fixations list.
        3. Calculates minor accumulated directed mask by subtracting the excluded directed mask
        from the accumulated directed mask.
        4. Calculates correlation between minor accumulated directed mask and excluded directed mask.
        5. Saves results to file.
        5. Repeats steps 2-5 for all directed masks in the relatable fixations list.
        """
        print(f"Performing leave-one-out cross-validation for {len(relatable_fixations_list)} directed masks")
        accumulated_directed_mask_dir = ACCUMULATED_DIRECTED_MASK_DIR
        accumulated_directed_mask_path = os.path.join(accumulated_directed_mask_dir,
                                                      f"{list_id}-accumulated-directed-mask.npy")
        minor_accumulated_directed_mask = np.load(accumulated_directed_mask_path)
        for index, relatable_fixations in enumerate(relatable_fixations_list):
            pid = relatable_fixations.pid
            exploration_id = relatable_fixations.exploration_id

            validation_result = self._get_validation_result()
            validation_scores = validation_result.validation_scores
            validation_score, score_index = self._find_validation_score(validation_scores, list_id, pid, exploration_id)
            directed_mask_score = None
            if validation_score:
                directed_mask_score = validation_score.dm_score

            if not directed_mask_score or self.config.validation_overwrite:
                print(f"Leaving out directed mask {index + 1}")
                directed_mask_file_path = get_directed_mask_file_path(pid, exploration_id)
                left_out_directed_mask = np.load(directed_mask_file_path)
                subtracted_directed_mask = self.accumulator.subtract_directed_mask(minor_accumulated_directed_mask,
                                                                              left_out_directed_mask)
                dm_correlation, dm_p_value = Validator._correlation_between_directed_masks(subtracted_directed_mask,
                                                                                           left_out_directed_mask)

                directed_mask_score = DirectedMaskScore(dm_correlation, dm_p_value)
                if validation_score:
                    validation_score.dm_score = directed_mask_score
                    validation_scores[score_index] = validation_score
                else:
                    validation_score = ValidationScore(list_id, pid, exploration_id, None, directed_mask_score)
                    validation_scores.append(validation_score)
                validation_result.save(self.file_path)

    def _loucv_heatmaps(self, list_id, relatable_fixations_list):
        """Performs leave-one-out cross-validation for heatmaps.
        1. Excludes one heatmap from the relatable fixations list.
        2. Calculates minor accumulated heatmap, accumulating all but the excluded heatmap.
        3. Calculates correlation between minor accumulated heatmap and excluded heatmap.
        4. Saves results to file.
        5. Repeats steps 1-4 for all directed masks in the relatable fixations list.
        """
        print(f"Performing leave-one-out cross-validation for {len(relatable_fixations_list)} heatmaps")
        for index, relatable_fixations in enumerate(relatable_fixations_list):
            pid = relatable_fixations.pid
            exploration_id = relatable_fixations.exploration_id

            validation_result = self._get_validation_result()
            validation_scores = validation_result.validation_scores
            validation_score, score_index = self._find_validation_score(validation_scores, list_id, pid, exploration_id)
            heatmap_score = None
            if validation_score:
                heatmap_score = validation_score.hm_score

            if not heatmap_score or self.config.validation_overwrite:
                print(f"Leaving out heatmap {index + 1}")
                left_out_relatable_fixations_list = [relatable_fixations]
                current_relatable_fixations_list = relatable_fixations_list.copy()
                current_relatable_fixations_list.pop(index)

                left_out_heatmap = self.plotter.create_heatmap_from_heat_points(
                    self.accumulator.relatable_fixations_list_to_heat_points(
                        left_out_relatable_fixations_list, WeightType.INTENSITY))
                current_accumulated_heatmap = self.plotter.create_heatmap_from_heat_points(
                    self.accumulator.relatable_fixations_list_to_heat_points(
                        current_relatable_fixations_list, WeightType.INTENSITY))

                hm_correlation, hm_p_value = Validator._correlation_between_heat_maps(current_accumulated_heatmap,
                                                                                      left_out_heatmap)

                heatmap_score = HeatMapScore(hm_correlation, hm_p_value)
                if validation_score:
                    validation_score.hm_score = heatmap_score
                    validation_scores[score_index] = validation_score
                else:
                    validation_score = ValidationScore(list_id, pid, exploration_id, heatmap_score, None)
                    validation_scores.append(validation_score)
                validation_result.save(self.file_path)

    def analyse_cross_validation_results(self, relatable_fixations_map):
        """Given the cross-validation results as correlation, this method calculates the
        standard deviation of all correlations.
        A low standard deviation suggests the existence of a pattern, while a high standard deviation suggests
        the absence of a pattern.
        """
        mapped_dm_correlation_values = dict()
        mapped_hm_correlation_values = dict()
        mapped_average_correlation_values = dict()
        for list_id, relatable_fixations_list in relatable_fixations_map.items():
            print(f"Validation result for {list_id}")
            validation_result = self._get_validation_result()
            filtered_validation_scores = self._filter_validation_scores_by_mapping(validation_result.validation_scores, list_id)
            dm_correlation_values = []
            hm_correlation_values = []
            average_correlation_values = []
            for filter_index, filtered_validation_score in enumerate(filtered_validation_scores):
                dm_corr = filtered_validation_score.dm_score.corr
                dm_correlation_values.append(dm_corr)
                print(f"Directed Mask Correlation {filter_index + 1}: {dm_corr}")
                hm_corr = filtered_validation_score.hm_score.corr
                hm_correlation_values.append(hm_corr)
                print(f"Heatmap Correlation {filter_index + 1}: {hm_corr}")
                avg_corr = statistics.mean([dm_corr, hm_corr])
                average_correlation_values.append(avg_corr)
                print(f"Average Correlation {filter_index + 1}: {avg_corr}")
            mapped_dm_correlation_values[list_id] = dm_correlation_values
            mapped_hm_correlation_values[list_id] = hm_correlation_values
            mapped_average_correlation_values[list_id] = average_correlation_values

            dm_stdev = statistics.stdev(dm_correlation_values)
            print(f"{list_id} - Directed Mask Standard Deviation: {dm_stdev}")
            print(f"{list_id} - Directed Mask Coefficient of Variation: {self._cv(dm_correlation_values)}")
            hm_stdev = statistics.stdev(hm_correlation_values)
            print(f"{list_id} - Heatmap Standard Deviation: {hm_stdev}")
            print(f"{list_id} - Heatmap Coefficient of Variation: {self._cv(hm_correlation_values)}")

        return mapped_dm_correlation_values, mapped_hm_correlation_values, mapped_average_correlation_values

    @staticmethod
    def _correlation_between_directed_masks(mask1, mask2):
        """Returns the correlation between two directed masks.
        Each vector in the mask is represented by its x and y coordinate.
        It is not possible to find a vector representation that reflects in one value.
        Thus, to calculate the correlation of vectors, we calculaate the correlation of both
        x and y coordinate separately and chose their average as the correlation of the vectors.
        """
        mask1_x_coordinates = mask1[:, :, 0]
        mask2_x_coordinates = mask2[:, :, 0]
        x_correlation, x_p_value = Validator._pearson_correlation_similarity(mask1_x_coordinates, mask2_x_coordinates)

        mask1_y_coordinates = mask1[:, :, 1]
        mask2_y_coordinates = mask2[:, :, 1]
        y_correlation, y_p_value = Validator._pearson_correlation_similarity(mask1_y_coordinates, mask2_y_coordinates)

        return statistics.mean([x_correlation, y_correlation]), statistics.mean([x_p_value, y_p_value])

    @staticmethod
    def _correlation_between_heat_maps(heatmap1, heatmap2):
        """Returns the correlation between two heatmaps and the corresponding p-value.
        """
        return Validator._pearson_correlation_similarity(heatmap1, heatmap2)

    @staticmethod
    def _pearson_correlation_similarity(np_2d_array1, np_2d_array_2):
        """Calculates pearson correlation if possible.

        args:
            - np_2d_array1: 2D numpy array.
            - np_2d_array2: 2D numpy array.

        returns:
            - pearson correlation between np_2d_array1 and np_2d_array2.
            - p_value of the pearson correlation.

        In case either of the input arrays has a constant value, the pearson correlation cannot be calculated.
        The return value will be the worst pearson correlation.
        An input array can have constant value when:
        - It is a heatmap and 0 fixation points were provided.
        - It is a directed mask and < 2 fixation points were provided.
        A saccade requires 2 fixation points to exist.
        """
        if (np_2d_array1 == np_2d_array1[0]).all() or (np_2d_array_2 == np_2d_array_2[0]).all():
            corr = p_value = 0
        else:
            corr, p_value = pearsonr(np_2d_array1.flatten(), np_2d_array_2.flatten())
        return corr, p_value

    def _get_validation_result(self):
        validation_result = ValidationResult()
        validation_result.load(self.file_path)
        return validation_result

    @staticmethod
    def _filter_validation_scores_by_mapping(validation_scores, mapping):
        filtered_validation_scores = []
        for validation_score in validation_scores:
            if validation_score.mapping == mapping:
                filtered_validation_scores.append(validation_score)
        return filtered_validation_scores

    @staticmethod
    def _find_validation_score(validation_result, mapping, pid, eid):
        for index, validation_score in enumerate(validation_result):
            if validation_score.mapping == mapping and validation_score.pid == pid and validation_score.eid == eid:
                return validation_score, index
        return None, None

    @staticmethod
    def _cv(data):
        mean = statistics.mean(data)
        stdev = statistics.stdev(data)
        return (stdev/mean)*100



