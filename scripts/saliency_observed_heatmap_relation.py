"""
This script prints and plots the relation between the saliency maps for a given image
and the task-based observed heatmap.
From this we can infer whether salient elements link to elements of interest for solving the task.
"""

import os.path
import statistics

import cv2
from matplotlib import pyplot as plt

from analysis.Differentiator import Differentiator
from analysis.Validator import Validator
from analysis.analysis_utils import parse_explorations, get_explorations_file_path, get_participant_analysis_plot_dir
from config import SALIENCE_IMG_DIR
from util import find_file_in_dir

task_2_thresh = 4
task_3_thresh = 2 * task_2_thresh


def saliency_observed_heatmap_relation():

    correlation_values = list()

    for pid in range(1, 17):
        explorations = parse_explorations(get_explorations_file_path(pid))

        for index, exploration in enumerate(explorations):

            if index < task_3_thresh:
                continue

            saliency_map_name = Differentiator._get_saliency_map_name(exploration.img_name)
            saliency_map_path = find_file_in_dir(saliency_map_name, SALIENCE_IMG_DIR)
            saliency_map = cv2.imread(saliency_map_path, cv2.IMREAD_GRAYSCALE)

            exploration_heatmap_path = os.path.join(get_participant_analysis_plot_dir(pid), f"{index}-heatmap-raw.png")
            exploration_heatmap = cv2.imread(exploration_heatmap_path, cv2.IMREAD_GRAYSCALE)

            corr, p = Validator._correlation_between_heat_maps(saliency_map, exploration_heatmap)

            correlation_values.append(corr)
            print(f"({index + 1}) {saliency_map_name}: {corr}")

    corr_mean = statistics.mean(correlation_values)
    corr_stdev = statistics.stdev(correlation_values)
    coefficient_of_variation = (corr_stdev / corr_mean) * 100

    print(f"Average correlation value: {round(corr_mean, 4)}")
    print(f"Standard deviation of correlation values: {round(corr_stdev, 4)}")
    print(f"Coefficient of variation of correlation values: {round(coefficient_of_variation, 4)}")

    fig = plt.figure(figsize=(10, 7))
    plt.boxplot(correlation_values)
    plt.show()


if __name__ == '__main__':
    saliency_observed_heatmap_relation()
