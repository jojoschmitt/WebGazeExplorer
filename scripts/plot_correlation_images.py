"""
This script is made to get a better feeling for the correlation results and how the correlation values change.
"""

import os
import cv2
from matplotlib import pyplot as plt

from analysis import Analyzer
from analysis.WeightType import WeightType
from config import SCRIPT_RESOURCES_DIR


def plot_correlations_based_on_real_heatmaps():
    evaluation_result = os.path.join(SCRIPT_RESOURCES_DIR, 'ValidationResult.txt')
    pos_max = (None, None, None)
    neg_max = (None, None, None)
    zero = (None, None, None)
    random_1 = (None, None, None)
    random_2 = (None, None, None)

    with open(evaluation_result, "r") as file:
        task_id = None
        for line in file:
            if 'Validation result' in line:
                task_id = int(line.split(' ')[-1].split('-')[-1])
            elif 'Heatmap Correlation' in line:
                img_pos = int(line.split(':')[0].split(' ')[-1])-1
                corr = float(line.split(':')[-1].strip())
                if pos_max[0] is None or corr > pos_max[0]:
                    pos_max = (corr, img_pos, task_id)
                if neg_max[0] is None or corr < neg_max[0]:
                    neg_max = (corr, img_pos, task_id)
                if zero[0] is None or abs(0-corr) < abs(0-zero[0]):
                    zero = (corr, img_pos, task_id)
                if '33' in line:
                    random_1 = (corr, img_pos, task_id)
                if '11' in line:
                    random_2 = (corr, img_pos, task_id)

    print(pos_max)
    print(neg_max)
    print(zero)
    print(random_1)
    print(random_2)
    val_results = [pos_max, neg_max, zero, random_1, random_2]

    analyzer = Analyzer.get_default_analyzer()

    relatable_fixations = analyzer.accumulator.get_relatable_fixations()
    relatable_fixations_map = analyzer.accumulator.map_relatable_fixations(relatable_fixations)

    results = []
    for val_res in val_results:
        hm, acc_hm = _get_heatmap_and_accumulated_heatmap(val_res, relatable_fixations_map, analyzer)
        results.append((hm, acc_hm, val_res[0]))
    _plot_results(results)


def _get_heatmap_and_accumulated_heatmap(val_res, relatable_fixations_map, analyzer):
    relatable_fixations_list = relatable_fixations_map[f'task-id-{val_res[2]}']

    pos_max_observation = relatable_fixations_list[val_res[1]]

    left_out_relatable_fixations_list = [pos_max_observation]
    current_relatable_fixations_list = relatable_fixations_list.copy()
    current_relatable_fixations_list.pop(val_res[1])

    left_out_heatmap = analyzer.plotter.create_heatmap_from_heat_points(
        analyzer.accumulator.relatable_fixations_list_to_heat_points(
            left_out_relatable_fixations_list, WeightType.INTENSITY))
    current_accumulated_heatmap = analyzer.plotter.create_heatmap_from_heat_points(
        analyzer.accumulator.relatable_fixations_list_to_heat_points(
            current_relatable_fixations_list, WeightType.INTENSITY))

    return left_out_heatmap, current_accumulated_heatmap


def _plot_results(res):
    # res = (heatmap, accumulated heatmap, correlation)
    num_columns = len(res)
    num_rows = 2  # One row for ground truth, one row for compared heatmaps

    #fig, axes = plt.subplots(num_rows, num_columns, figsize=(32, 8))  # High resolution
    fig, axes = plt.subplots(num_rows, num_columns, figsize=(16, 6))  # Paper
    plt.subplots_adjust(wspace=0.2, hspace=0)

    for i, (heatmap, acc_heatmap, corr) in enumerate(res):
        # Plot ground truth heatmap
        axes[0, i].imshow(heatmap, cmap='gray', interpolation='nearest', vmin=0, vmax=255)
        axes[0, i].set_title(f'Left out')

        # Plot compared heatmap
        axes[1, i].imshow(acc_heatmap, cmap='gray', interpolation='nearest', vmin=0, vmax=255)
        axes[1, i].set_title("Accumulated")

        # Print correlation value
        correlation_value = corr
        axes[1, i].text(0.5, -0.2, f'Corr: {correlation_value:.4f}', size=10, weight='bold', ha="center", transform=axes[1, i].transAxes)

    # Hide x and y ticks for all subplots
    for ax in axes.flatten():
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    plt.show()


def plot_correlations_from_forged_heatmaps():
    correlation_heatmap_dir = os.path.join(SCRIPT_RESOURCES_DIR, 'correlation_heatmaps')
    h_gt = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-gt.png'), cv2.IMREAD_GRAYSCALE)
    h_overlap = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-overlap.png'),
                           cv2.IMREAD_GRAYSCALE)
    h_partial_overlap_1 = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-partial-overlap-1.png'),
                                     cv2.IMREAD_GRAYSCALE)
    h_partial_overlap_2 = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-partial-overlap-2.png'),
                                     cv2.IMREAD_GRAYSCALE)
    h_partial_overlap_3 = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-partial-overlap-3.png'),
                                     cv2.IMREAD_GRAYSCALE)
    h_partial_overlap_4 = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-partial-overlap-4.png'),
                                     cv2.IMREAD_GRAYSCALE)
    h_partial_overlap_5 = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-partial-overlap-5.png'),
                                     cv2.IMREAD_GRAYSCALE)
    h_distinct = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-distinct.png'), cv2.IMREAD_GRAYSCALE)
    h_close = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-close.png'), cv2.IMREAD_GRAYSCALE)
    h_black = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-black.png'), cv2.IMREAD_GRAYSCALE)
    h_white = cv2.imread(os.path.join(correlation_heatmap_dir, 'heatmap-white.png'), cv2.IMREAD_GRAYSCALE)

    heatmaps = {
        'Ground Truth': h_gt,
        'Overlap': h_overlap,
        'Partial Overlap 1': h_partial_overlap_1,
        'Partial Overlap 2': h_partial_overlap_2,
        'Partial Overlap 3': h_partial_overlap_3,
        'Partial Overlap 4': h_partial_overlap_4,
        'Partial Overlap 5': h_partial_overlap_5,
        'Close': h_close,
        'Distinct': h_distinct,
        'Full Black': h_black,
        'Full White': h_white
    }

    analyzer = Analyzer.get_default_analyzer()

    gt_title = 'Ground Truth'
    h_gt = heatmaps[gt_title]
    correlations = dict()
    for title, heatmap in heatmaps.items():
        corr, p = analyzer.validator._correlation_between_heat_maps(h_gt, heatmap)
        correlations[title] = corr
    _plot_result(correlations, heatmaps)


def _plot_result(correlations, heatmaps):
    num_columns = len(heatmaps)
    num_rows = 2  # One row for ground truth, one row for compared heatmaps

    title_gt = 'Ground Truth'
    h_gt = heatmaps[title_gt]

    #fig, axes = plt.subplots(num_rows, num_columns, figsize=(32, 8))  # High resolution
    fig, axes = plt.subplots(num_rows, num_columns, figsize=(16, 4))  # Paper
    plt.subplots_adjust(wspace=0.2, hspace=0)

    for i, (title, heatmap) in enumerate(heatmaps.items()):
        # Plot ground truth heatmap
        axes[0, i].imshow(h_gt, cmap='gray', interpolation='nearest', vmin=0, vmax=255)
        axes[0, i].set_title(f'{title_gt}')

        # Plot compared heatmap
        axes[1, i].imshow(heatmap, cmap='gray', interpolation='nearest', vmin=0, vmax=255)
        axes[1, i].set_title(title)

        # Print correlation value
        correlation_value = correlations[title]
        axes[1, i].text(0.5, -0.2, f'Corr: {correlation_value:.4f}', size=10, weight='bold', ha="center", transform=axes[1, i].transAxes)

    # Hide x and y ticks for all subplots
    for ax in axes.flatten():
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # Requires observations and a <repo-roto>/scripts/script_resources/ValidationResult.txt
    # like the one we provided for dummy.
    # plot_correlations_based_on_real_heatmaps()

    # All required resources available within the repository.
    plot_correlations_from_forged_heatmaps()
