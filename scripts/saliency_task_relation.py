"""
This script prints and plots the relation between the AOIs for task 3 images and their saliency maps.
From this we can infer whether salient elements link to elements of interest for solving the task.
"""

import os.path
import statistics

import cv2
import matplotlib.pyplot as plt

from analysis.Validator import Validator
from config import SCRIPT_RESOURCES_DIR, SALIENCE_IMG_DIR
from util import list_files


def saliency_task_relation():
    aoi_heatmaps_dir = os.path.join(SCRIPT_RESOURCES_DIR, 'aoi_heatmaps')
    aoi_heatmap_names = list_files(aoi_heatmaps_dir)
    assert len(aoi_heatmap_names) > 0
    saliency_maps_dir = SALIENCE_IMG_DIR
    assert os.path.exists(saliency_maps_dir)
    saliency_map_names = list_files(saliency_maps_dir)
    assert len(saliency_map_names) >= 96

    correlation_values = list()

    for index, aoi_heatmap_name in enumerate(aoi_heatmap_names):
        aoi_heatmap_path = os.path.join(aoi_heatmaps_dir, aoi_heatmap_name)
        saliency_map_name = aoi_heatmap_name.split('-')[0] + "-saliency.png"
        saliency_map_path = os.path.join(saliency_maps_dir, saliency_map_name)
        aoi_heatmap = cv2.imread(aoi_heatmap_path, cv2.IMREAD_GRAYSCALE)
        saliency_map = cv2.imread(saliency_map_path, cv2.IMREAD_GRAYSCALE)
        corr, p = Validator._correlation_between_heat_maps(aoi_heatmap, saliency_map)

        correlation_values.append(corr)
        print(f"({index+1}) {aoi_heatmap_name}: {corr}")

    corr_mean = statistics.mean(correlation_values)
    corr_stdev = statistics.stdev(correlation_values)
    coefficient_of_variation = (corr_stdev / corr_mean) * 100

    print(f"Average correlation value: {round(corr_mean,4)}")
    print(f"Standard deviation of correlation values: {round(corr_stdev, 4)}")
    print(f"Coefficient of variation of correlation values: {round(coefficient_of_variation, 4)}")

    fig = plt.figure(figsize=(10, 7))
    plt.boxplot(correlation_values)
    plt.show()


if __name__ == '__main__':
    saliency_task_relation()