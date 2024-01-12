import math
import os.path

import cv2
import numpy as np

from analysis.AccumulationMapping import AccumulationMapping
from analysis.AnalysisConfiguration import AnalysisConfiguration
from analysis.extractors.BivariateSplineExtractor import BivariateSplineExtractor
from analysis.Plotter import Plotter
from analysis.RelatableFixations import RelatableFixations
from analysis.SimpleFixation import SimpleFixation
from analysis.WeightType import WeightType
from analysis.HeatPoint import HeatPoint
from analysis.analysis_utils import parse_explorations, get_explorations_file_path, parse_fixations, \
    get_difference_fixations_file_path, get_movements_file_path, filter_fixations_for_exploration, \
    DIRECTED_MASK_SIGNATURE, get_directed_mask_file_path, get_directed_masks_dir
from config import ACCUMULATED_PLOT_DIR, ORIGINAL_IMG_DIR, ACCUMULATED_DIRECTED_MASK_DIR, MIDDLE_FIXATION_INTENSITY, \
    ACCUMULATED_SALIENCE_PLOT_DIR
from experiment.Experiment import Experiment
from experiment.Image import Image
from experiment.Task import Task
from util import normalize_value, find_file_in_dir


SimpleFixationsMap = dict[str, list[SimpleFixation]]
RelatableFixationsMap = dict[str, list[RelatableFixations]]
TaskId = str
TaskSimpleFixationsMap = dict[TaskId, list[SimpleFixation]]


class Accumulator:
    def __init__(self, config, plotter):
        self.config: AnalysisConfiguration = config
        self.plotter: Plotter = plotter

    def get_relatable_fixations(self):
        """Collects all fixations from the given PIDs.
        Remembers which fixation belongs to which PID and image i.e. task and specification.
        Only exploration referencing fixations are considered (fixations while an image is visible).

        returns:
            - A list of RelatableFixations
        """
        print(f"Creating relatable fixations")
        relatable_fixations = []
        for pid in self.config.participants:
            explorations = parse_explorations(get_explorations_file_path(pid))
            if self.config.saliency:
                fixations = parse_fixations(get_difference_fixations_file_path(pid))
            else:
                fixations = parse_fixations(get_movements_file_path(pid))
            for index, exploration in enumerate(explorations):
                exploration_based_fixations = filter_fixations_for_exploration(exploration, fixations)
                trial_nr = index+1
                quotient, remainder = divmod(trial_nr, 4)
                if remainder == 0:
                    task_id = quotient
                else:
                    task_id = quotient+1
                task = Task(task_id, pid)
                img_round = trial_nr - 4 * (task_id-1)
                img_id = Experiment.get_img_id(pid, task, img_round)
                img = Image(img_id, task_id)
                relatable_fixations.append(RelatableFixations(pid, img, index, exploration_based_fixations))

        return relatable_fixations

    def map_relatable_fixations(self, relatable_fixations: list[RelatableFixations]):
        match self.config.accumulation_mapping:
            case AccumulationMapping.TASK:
                relatable_fixations_map = self._map_relatable_fixations_to_task(relatable_fixations)
            case AccumulationMapping.SPECIFICATION:
                relatable_fixations_map = self._map_relatable_fixations_to_specification(relatable_fixations)
            case _:
                raise ValueError(f"This accumulation mapping is not allowed: {self.config.accumulation_mapping}")
        # Filter out keys with an empty relatable fixations list
        return {key: value for key, value in relatable_fixations_map.items() if value}

    def _map_relatable_fixations_to_task(self, relatable_fixations: list[RelatableFixations]):
        print(f"Mapping relatable fixations to tasks")
        accumulated_relatable_fixations = dict()
        key = "task-id-{}"
        for task_id in range(1, 4):
            accumulated_relatable_fixations[key.format(task_id)] = []
        for relatable_fixation in relatable_fixations:
            key_value = key.format(relatable_fixation.image.task_id)
            accumulated_relatable_fixations[key_value].append(relatable_fixation)
        return accumulated_relatable_fixations

    def _map_relatable_fixations_to_specification(self, relatable_fixations: list[RelatableFixations]):
        print(f"Mapping relatable fixations to image specifications per task")
        SPECIFICATIONS = {
            1: ["community", "ecommerce", "entertainment", "informational"],
            2: ["contact-form", "downloadable-content", "information-reading", "login", "checkout", "posting-content",
                "registration", "visual-media-consumption"],
            3: ["career", "add-to-cart", "landing-page", "login", "logout", "checkout", "posting-content", "registration"]
        }
        accumulated_relatable_fixations = dict()
        key = "specification-{}-task-{}"
        for task_id in SPECIFICATIONS.keys():
            for specification in SPECIFICATIONS[task_id]:
                accumulated_relatable_fixations[key.format(specification, task_id)] = []
        for relatable_fixation in relatable_fixations:
            task_id = relatable_fixation.image.task_id
            specification = SPECIFICATIONS[task_id][relatable_fixation.image.specification_id-1]
            key_value = key.format(specification, task_id)
            accumulated_relatable_fixations[key_value].append(relatable_fixation)
        return accumulated_relatable_fixations

    def relatable_fixations_list_to_simple_fixations(self, relatable_fixations_list: list[RelatableFixations]) -> list[SimpleFixation]:
        return [simple_fixation for relatable_fixations in relatable_fixations_list for simple_fixation in relatable_fixations.fixations]

    def relatable_fixations_list_to_heat_points(self, relatable_fixations_list, weight_type):
        simple_fixations = self.relatable_fixations_list_to_simple_fixations(relatable_fixations_list)

        def get_intensity(fixation):
            if weight_type == WeightType.CONSTANT:
                return MIDDLE_FIXATION_INTENSITY
            elif weight_type == WeightType.INTENSITY:
                return fixation.duration
            elif weight_type == WeightType.ORDER:
                flip, min_weight, max_weight = self._get_flipped_min_max_weight(simple_fixations)
                return flip(fixation.timestamp_us)
            else:
                raise ValueError(f"This weight type is not supported to calculate the intensity of a single fixation ({weight_type})")

        heat_points = []
        for fixation in simple_fixations:
            heat_points.append(HeatPoint(fixation.norm_x, fixation.norm_y, get_intensity(fixation)))

        return heat_points

    def accumulated_fixations(self, accumulated_fixations: RelatableFixationsMap, accumulated_plot_dir):
        """Calculates new heat points based on the intensity values of the accumulated fixations.

        Plot heatmap from accumulated fixation intensities.
        Extract new heat points from the heatmap.

        args:
            - accumulated_fixations: Dict that holds lists of relatable fixations. The lists are grouped based on the
            RelatableFixationsMap used for the accumulated fixations. Any RelatableFixationsMap can be used.
            - accumulated_plot_dir: Defines the directory where all accumulated plots will be saved.
            - weight_type: The type by which the heat sources' intensities are defined.
            - overwrite: If true, always generates new data with a new file,
            otherwise only generates new data and a new file if no existing matching file with data exists.

        returns:
            - New dict that holds a lists of heat points for each key in the provided RelatableFixationsMap.
        """
        accumulated_weight_type = self.config.accumulated_weight_type
        assert accumulated_weight_type == WeightType.CONSTANT or accumulated_weight_type == WeightType.INTENSITY or accumulated_weight_type == WeightType.ORDER
        intensity_based_heatmap_file_name_template = "{}-intensity-based-heatmap.png"
        if accumulated_weight_type == WeightType.CONSTANT:
            print(f"Generating unweighted accumulated fixations")
            heatmap_file_name_template = "{}-unweighted-heatmap.png"
            scanpath_file_name_template = "{}-unweighted-scanpath.png"
        elif accumulated_weight_type == WeightType.INTENSITY:
            print(f"Generating intensity based accumulated fixations")
            heatmap_file_name_template = "{}-intensity-based-heatmap.png"
            scanpath_file_name_template = "{}-intensity-based-scanpath.png"
        else:
            print(f"Generating order based accumulated fixations")
            heatmap_file_name_template = "{}-order-based-heatmap.png"
            scanpath_file_name_template = "{}-order-based-scanpath.png"
        print(f"The generation process will always include the generation of accumulated fixations for building directed heatmaps.")

        accumulated_heat_sources = dict()
        for list_id, relatable_fixations_list in accumulated_fixations.items():
            print(f"Generating accumulated fixations for {list_id}")

            # Always plot intensity based accumulated heatmap for directed heatmap
            heat_points = self.relatable_fixations_list_to_heat_points(relatable_fixations_list, WeightType.INTENSITY)

            heatmap_plot_file_path = os.path.join(accumulated_plot_dir, intensity_based_heatmap_file_name_template.format(list_id))
            self.plotter.plot_accumulated_heatmap_from_heat_points(heatmap_plot_file_path, heat_points)

            # Plot additional heatmap if required to be able to plot scanpath
            # (e.g. order based accumulated scanpath needs order based accumulated heatmap)
            if accumulated_weight_type != WeightType.INTENSITY:
                heat_points = self.relatable_fixations_list_to_heat_points(relatable_fixations_list, accumulated_weight_type)

                heatmap_plot_file_path = os.path.join(accumulated_plot_dir, heatmap_file_name_template.format(list_id))
                self.plotter.plot_accumulated_heatmap_from_heat_points(heatmap_plot_file_path, heat_points)

            extractor = BivariateSplineExtractor(self.config.accumulation_overwrite)
            heat_sources = extractor.get_heat_sources_from_heatmap(heatmap_plot_file_path)
            scanpath_plot_file_path = os.path.join(accumulated_plot_dir, scanpath_file_name_template.format(list_id))
            self.plotter.plot_accumulated_scanpath_from_heat_points(scanpath_plot_file_path, heat_sources)
            accumulated_heat_sources[list_id] = heat_sources

        return accumulated_heat_sources

    def generate_accumulated_fixations(self, relatable_fixations_map):
        if self.config.saliency:
            accumulated_plot_dir = ACCUMULATED_SALIENCE_PLOT_DIR
            print(f"Initializing generation of saliency considered accumulated fixations.")
        else:
            accumulated_plot_dir = ACCUMULATED_PLOT_DIR
            print(f"Initializing generation of accumulated fixations.")
        if not os.path.exists(accumulated_plot_dir):
            print(f"Creating directory for accumulated plots: ({accumulated_plot_dir})")
            if self.config.saliency:
                os.mkdir(ACCUMULATED_PLOT_DIR)
            os.mkdir(accumulated_plot_dir)

        self.accumulated_fixations(relatable_fixations_map, accumulated_plot_dir)

    def generate_directed_masks(self, relatable_fixations: list[RelatableFixations]):
        for relatable_fixation in relatable_fixations:
            pid = relatable_fixation.pid
            directed_masks_dir = get_directed_masks_dir(pid)
            if not os.path.exists(directed_masks_dir):
                os.makedirs(directed_masks_dir)

            original_img_path = find_file_in_dir(relatable_fixation.image.get_name(), ORIGINAL_IMG_DIR)

            directed_mask_file_path = get_directed_mask_file_path(pid, relatable_fixation.exploration_id)
            if not os.path.exists(directed_mask_file_path) or self.config.directed_mask_overwrite:
                # Generate a directed mask and save it to file
                directed_mask = self.generate_directed_mask(original_img_path, relatable_fixation.fixations, self.config.directed_weight_type)
                np.save(directed_mask_file_path, directed_mask)

    def generate_accumulated_directed_masks(self, relatable_fixations_map: RelatableFixationsMap):
        accumulated_directed_mask_dir = ACCUMULATED_DIRECTED_MASK_DIR
        if not os.path.exists(accumulated_directed_mask_dir):
            os.mkdir(accumulated_directed_mask_dir)

        accumulated_directed_masks = []

        for list_id, relatable_fixations_list in relatable_fixations_map.items():
            accumulated_directed_mask_path = os.path.join(accumulated_directed_mask_dir, f"{list_id}-accumulated-directed-mask.npy")
            if os.path.exists(accumulated_directed_mask_path) and not self.config.directed_mask_overwrite:
                accumulated_directed_masks.append(np.load(accumulated_directed_mask_path))
            else:
                directed_masks = []

                for relatable_fixation in relatable_fixations_list:
                    pid = relatable_fixation.pid
                    directed_mask_file_path = get_directed_mask_file_path(pid, relatable_fixation.exploration_id)
                    if not os.path.exists(directed_mask_file_path):
                        raise FileNotFoundError(f"Could not find directed mask: {directed_mask_file_path}")
                    directed_masks.append(np.load(directed_mask_file_path))

                accumulated_directed_mask = self.accumulate_directed_masks(directed_masks)
                accumulated_directed_masks.append(accumulated_directed_mask)
                np.save(accumulated_directed_mask_path, accumulated_directed_mask)

        return accumulated_directed_masks

    def accumulate_directed_masks(self, directed_masks):
        """Cumulatively adds up vectors at the same position for each directed mask.
        """
        accumulated_directed_mask = directed_masks[0]
        shape = accumulated_directed_mask.shape
        height, width, _ = shape

        vectorized_combine_directed_mask_values = np.vectorize(self._combine_directed_mask_values, signature=DIRECTED_MASK_SIGNATURE)

        print(f"Planned directed mask accumulations: {len(directed_masks)-1}")
        for index, directed_mask in enumerate(directed_masks[1:]):
            print(f"Current directed mask accumulation: {index+1}")
            if shape != directed_mask.shape:
                raise ValueError(f"Directed masks must have the same shape {shape} != {directed_mask.shape}")

            accumulated_directed_mask = vectorized_combine_directed_mask_values(accumulated_directed_mask, directed_mask)

        return accumulated_directed_mask

    def subtract_directed_mask(self, accumulated_directed_mask, directed_mask):
        """Subtracts directed mask vectors from accumulated directed mask vectors at the same position.
        """
        vectorized_subtract_directed_mask_values = np.vectorize(self._subtract_directed_mask_values, signature=DIRECTED_MASK_SIGNATURE)
        subtracted_directed_mask = vectorized_subtract_directed_mask_values(accumulated_directed_mask, directed_mask)
        return subtracted_directed_mask

    def generate_directed_mask(self, original_img_path, filtered_fixations: list[SimpleFixation], weight_type):
        """Generates a directed mask from a scanpath.
        The directed mask covers the whole size of the original image with additional information.
        For each pixel, the mask adds information about its direction and its affinity to this direction.

        Initially, the points in the mask do not have any direction or affinity.
        For each saccade, pixels in the range of the starting fixation are struck in the direction of the saccade.
        The intensity of a stroke is given by the occurrence of the starting fixation in time which dictates the
        affinity of pixels in range.
        The earlier the saccade, the more important it is and thus the higher its affinity will be.
        Direction and affinity is calculated additively.

        args:
            - original_img_path: The absolute path to the original image to get the shape of the directed mask.
            - filtered_fixations: A list of simple fixations ot find
            the saccades between them and influence the directed mask.
            - weight_type: Determines by which weight type the vector strength is influenced

        returns:
            - A directed mask. Basically a 2D numpy array where each point has a vector value of (direction, strength).
        """
        # Load the original image
        original_img = cv2.imread(original_img_path)
        width = original_img.shape[1]
        height = original_img.shape[0]

        # Initialize mask (2D array) with all zero directions and strengths (0, 0)
        directed_mask = np.zeros((width * height, 2))
        directed_mask = directed_mask.reshape((height, width, 2))
        # Create a grid of coordinates for the 2D array
        x_vector, y_vector = np.meshgrid(np.arange(directed_mask.shape[1]), np.arange(directed_mask.shape[0]))

        if not filtered_fixations:
            return directed_mask

        flip = None
        min_weight = None
        max_weight = None

        if weight_type == WeightType.ORDER:
            flip, min_weight, max_weight = self._get_flipped_min_max_weight(filtered_fixations)

        num_filtered_fixations = len(filtered_fixations)
        print(f"Number of fixations to process: {num_filtered_fixations - 1}")
        for fixation_index, fixation in enumerate(filtered_fixations):
            if fixation_index < num_filtered_fixations - 1:
                print(f"Processing fixation: {fixation_index + 1}")
                next_fixation: SimpleFixation = filtered_fixations[fixation_index + 1]
                vector_origin = (fixation.norm_x * width, fixation.norm_y * height)
                vector_destination = (next_fixation.norm_x * width, next_fixation.norm_y * height)

                vector = (vector_destination[0] - vector_origin[0], vector_destination[1] - vector_origin[1])
                vector_len = math.sqrt(vector[0]**2 + vector[1]**2)
                assert vector_len != 0
                unit_vector = (vector[0] / vector_len, vector[1] / vector_len)

                if weight_type == WeightType.ORDER:
                    vector_intensity = normalize_value(flip(fixation.timestamp_us), min_weight, max_weight, 1, 256)
                elif weight_type == WeightType.DISTANCE:
                    vector_intensity = vector_len
                elif weight_type == WeightType.INTENSITY:
                    vector_intensity = normalize_value(fixation.duration, min_weight, max_weight, 1, 256)
                else:
                    vector_intensity = 50

                vector = (unit_vector[0] * vector_intensity, unit_vector[1] * vector_intensity)

                vector_range = vector_intensity

                # Find points in range of vector
                # Calculate all Euclidean distances from the vectors origin
                distance_vector = np.sqrt((x_vector - vector_origin[0]) ** 2 + (y_vector - vector_origin[1]) ** 2)
                # Find the indices of points within the given range
                indices_in_vector_range = np.where(distance_vector <= vector_range)

                points_in_range = []
                for i in range(len(indices_in_vector_range[0])):
                    points_in_range.append((indices_in_vector_range[0][i], indices_in_vector_range[1][i]))

                # Identify values for each index
                values_in_vector_range = directed_mask[indices_in_vector_range]
                # Remember the distances for each index
                distances_to_vector_origin = distance_vector[indices_in_vector_range]

                num_points_in_range = len(points_in_range)
                print(f"Influencing {num_points_in_range} vectors for fixation {fixation_index + 1}")
                for i in range(num_points_in_range):
                    #print(f"index {points_in_range[i]}; value {values_in_vector_range[i]}; distance {distances_to_vector_origin[i]}")
                    directed_mask[points_in_range[i]] = self._influence_vector(values_in_vector_range[i], vector, distances_to_vector_origin[i], vector_range)

        return directed_mask

    def _get_flipped_min_max_weight(self, simple_filtered_fixations):
        fixation_timestamps = [fixation.timestamp_us for fixation in simple_filtered_fixations]
        min_fixation_timestamp = min(fixation_timestamps)
        max_fixation_timestamp = max(fixation_timestamps)

        def flip(value):
            flipper = max_fixation_timestamp + 1
            return abs(value - flipper)

        # Flip timestamps to make early occurring fixations worth more than later occurring ones
        flipped_min_timestamp = flip(max_fixation_timestamp)
        flipped_max_timestamp = flip(min_fixation_timestamp)
        return flip, flipped_min_timestamp, flipped_max_timestamp

    def _influence_vector(self, influenced_vector: tuple, influencing_vector: tuple, vector_distance: float, influencing_vector_range: int) -> tuple:
        """Influences vectors in range of influencing vector. Uses a linear function to reduce
        the strength of influence the further the influenced vector is away from the influencing vector.

        args:
            - influenced_vector: One vector that is in range of the influencing vector and is influenced by it.
            - influencing_vector: The one vector extracted from the current saccade that influences surrounding vectors.
            - vector_distance: The distance of the influencing vector to the influenced vector.
            - influencing_vector_range: The range in which the influencing vector influences other vectors.

        returns:
            - The influenced vector after being influenced.
        """
        def _strength_at_range(current_distance, max_range, max_strength):
            return max_strength - (max_strength / max_range) * current_distance

        influencing_vector_strength = math.sqrt(influencing_vector[0] ** 2 + influencing_vector[1] ** 2)
        strength_at_range = _strength_at_range(vector_distance, influencing_vector_range, influencing_vector_strength)
        assert strength_at_range != 0
        influencing_unit_vector = (influencing_vector[0] / influencing_vector_strength, influencing_vector[1] / influencing_vector_strength)
        vector_influence = (influencing_unit_vector[0] * strength_at_range, influencing_unit_vector[1] * strength_at_range)
        added_vec = (influenced_vector[0] + vector_influence[0], influenced_vector[1] + vector_influence[1])

        return added_vec

    def _combine_directed_mask_values(self, vec1, vec2):
        added_vec = vec1[0] + vec2[0], vec1[1] + vec2[1]
        return np.array(added_vec)

    def _subtract_directed_mask_values(self, vec_minuend, vec_subtrahend):
        subtracted_vec = vec_minuend[0] - vec_subtrahend[0], vec_minuend[1] - vec_subtrahend[1]
        return np.array(subtracted_vec)
