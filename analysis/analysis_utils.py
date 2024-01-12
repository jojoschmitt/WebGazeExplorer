import os

import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

from analysis.Analyzer import Analyzer
from analysis.Exploration import Exploration
from analysis.Movement import Movement
from config import ANALYSIS_DATA_DIR, EXPERIMENT_DATA_DIR, ANALYSIS_PLOT_DIR

DIRECTED_MASK_SIGNATURE = '(2),(2)->(2)'


def find_close_dividers(target_divider, values):
    """Finds the closest two dividers to the target divider that divide each value with a remainder of 0.
    Currently limited to 2 values.
    """
    assert len(values) == 2
    x_divider_found = False
    y_divider_found = False
    dividers_found = x_divider_found and y_divider_found
    x_divider = target_divider
    y_divider = target_divider
    distance = 0
    increase_range = True
    while not dividers_found:
        if not x_divider_found:
            x_divider = target_divider + distance
            if values[0] % x_divider == 0:
                x_divider_found = True
        if not y_divider_found:
            y_divider = target_divider + distance
            if values[1] % y_divider == 0:
                y_divider_found = True
        if increase_range:
            distance = abs(distance) + 1
            increase_range = False
        else:
            distance *= -1
            increase_range = True
        dividers_found = x_divider_found and y_divider_found
    return x_divider, y_divider


def parse_fixations(movements_file_path) -> list[Movement]:
    fixations = []
    with open(movements_file_path, 'r') as movements_file:
        header_line = movements_file.readline()  # Read off header line
        for line in movements_file:
            movement = Movement.from_csv(line)
            if movement.is_fixation() and _is_fixation_on_display_area(movement):
                fixations.append(movement)
    return fixations


def parse_explorations(explorations_file_path) -> list[Exploration]:
    explorations = []
    with open(explorations_file_path, 'r') as explorations_file:
        header_line = explorations_file.readline()  # Read off header line
        exploration = Exploration.create_exploration()
        for line in explorations_file:
            exploration.attribute_from_tsv(line)
            # Create new exploration if the current one is completed
            if exploration.is_complete():
                explorations.append(exploration)
                exploration = Exploration.create_exploration()
    for i in range(len(explorations)-1):
        assert explorations[i].trial_end < explorations[i+1].trial_start
    return explorations


def filter_fixations_for_exploration(exploration: Exploration, fixations: list[Movement]) -> list[Movement]:
    """Filters fixations for an exploration/image.
    Fixations are passing the filter when they occur during the actual exploration i.e. while the image is visible.
    After that, the first fixation is filtered out because it is not influenced by a stimulus on the image.
    Also, the last fixation is filtered out in case its duration is outstandingly higher than every other fixation's
    duration because this indicates lingering attention caused by searching the button to end the exploration phase.
    """
    filtered_fixations = []
    for fixation in fixations:
        if exploration.img_online < fixation.timestamp_us < exploration.img_offline:
            filtered_fixations.append(fixation)
    if len(filtered_fixations) >= 3:
        filtered_fixations = _remove_last_fixation_if_positive_outlier(filtered_fixations[1:])
    return filtered_fixations


def _remove_last_fixation_if_positive_outlier(fixations):
    """Uses zscore to determine if the last fixation is a positive outlier.
    The z-score (or standard score) quantifies how many standard deviations a particular data point is away from mean.

    With only few data points e.g. 3, the zscore of one positive outlier stays fairly low due to the high impact of
    the outlier on the mean and hence the standard deviation.
    Since we have explorations with only few fixations, our threshold needs to be quite low.
    """
    fixation_durations = [fixation.duration for fixation in fixations]
    if max(fixation_durations) > fixation_durations[-1]:
        return fixations
    z_scores = np.array(stats.zscore(fixation_durations))
    threshold = 1.2
    outlier_indices = np.where(z_scores > threshold)
    last_fixation_index = len(fixation_durations)-1
    if last_fixation_index in outlier_indices[0]:
        return fixations[:-1]
    else:
        return fixations


def _is_fixation_on_display_area(fixation):
    """Raw gaze data from the Tobii SDK might include gaze points outside the display area.
    We are filtering those out here because there is no sense in plotting points outside the image.
    """
    if 0 <= fixation.average_gaze_point2d_x <= 1 and 0 <= fixation.average_gaze_point2d_y <= 1:
        return True
    return False


def plot_points_on_img(points, img_path, colored_source=True):
    if colored_source:
        flag = cv2.IMREAD_COLOR
    else:
        flag = cv2.IMREAD_GRAYSCALE
    img = cv2.imread(img_path, flag)
    fig, ax = plt.subplots(figsize=(img.shape[1] / 100, img.shape[0] / 100))
    ax.imshow(img, cmap='gray', vmin=0, vmax=255)
    for point in points:
        ax.scatter(point.x, point.y, c='red', marker='o')
    plt.axis('off')
    plt.show()


def get_participant_experiment_data_dir(pid):
    return os.path.join(EXPERIMENT_DATA_DIR, str(pid))


def get_participant_analysis_data_dir(pid):
    return os.path.join(ANALYSIS_DATA_DIR, str(pid))


def get_participant_analysis_plot_dir(pid):
    return os.path.join(ANALYSIS_PLOT_DIR, str(pid))


def get_movements_file_path(pid):
    return os.path.join(get_participant_analysis_data_dir(pid), "movements.csv")


def get_explorations_file_path(pid):
    return os.path.join(get_participant_analysis_data_dir(pid), "explorations.tsv")


def get_salience_considered_plot_dir(pid):
    return os.path.join(get_participant_analysis_plot_dir(pid), "salience_considered")


def get_salience_considered_data_dir(pid):
    return os.path.join(get_participant_analysis_data_dir(pid), "salience_considered")


def get_difference_fixations_file_path(pid):
    return os.path.join(get_salience_considered_data_dir(pid), "difference_fixations.csv")


def get_directed_masks_dir(pid):
    return os.path.join(get_participant_analysis_data_dir(pid), "directed_masks")


def get_directed_mask_file_path(pid, exploration_index):
    return os.path.join(get_directed_masks_dir(pid), f"{exploration_index}-directed-mask.npy")


def get_validation_analysis_file_path(accumulation_mapping):
    return os.path.join(ANALYSIS_PLOT_DIR, f"{accumulation_mapping}-correlation-boxplot.png")
