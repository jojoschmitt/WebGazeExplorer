"""
This script gives a visual comparison on the performance of several different extractors.
"""

import os.path
from datetime import datetime

import cv2
from matplotlib import pyplot as plt

from analysis.extractors.BivariateSplineExtractor import BivariateSplineExtractor
from analysis.extractors.ConcurrentHeatSourceEliminationExtractor import ConcurrentHeatSourceEliminationExtractor
from analysis.extractors.HeatSourceEliminationExtractor import HeatSourceEliminationExtractor
from analysis.extractors.UnivariateSplineExtractor import UnivariateSplineExtractor
from config import SALIENCE_IMG_DIR, ANALYSIS_PLOT_DIR
from util import list_files, find_file_in_dir, repo_root


def compare_extractors(extractors, heatmap_paths):
    res_dir = os.path.join(repo_root, 'scripts', 'extractor_comparisons')
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)
    for heatmap_path in heatmap_paths:
        output_file_path = os.path.join(res_dir, f'extracted-heat-sources-{os.path.basename(os.path.dirname(heatmap_path))}-{os.path.basename(heatmap_path)}')
        elapsed_times = []

        heatmap = cv2.imread(heatmap_path, cv2.IMREAD_GRAYSCALE)
        size = 5
        extractor_count = len(extractors)
        fig, axs = plt.subplots(1, extractor_count, figsize=(size*extractor_count, size))

        for index, extractor in enumerate(extractors):
            t0 = datetime.now().timestamp()
            extracted_heat_sources = extractor.get_heat_sources_from_heatmap(heatmap_path)
            elapsed_time = datetime.now().timestamp() - t0
            elapsed_times.append(elapsed_time)

            for extracted_heat_source in extracted_heat_sources:
                axs[index].imshow(heatmap, cmap='gray')
                extractor_name = str(extractor.__class__).split('.')[-2]
                axs[index].set_title(f"{extractor_name}: {elapsed_time:.2f} s")
                axs[index].plot(extracted_heat_source.x, extracted_heat_source.y, 'ro', markersize=1)

        plt.tight_layout()
        plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
        # plt.show()


def get_saliency_map_paths():
    file_names = list_files(SALIENCE_IMG_DIR)
    saliency_map_paths = []
    for name in file_names:
        if ".gitignore" in name:
            continue
        saliency_map_paths.append(find_file_in_dir(name, SALIENCE_IMG_DIR))
    return saliency_map_paths


def get_observation_heatmap_paths():
    heatmap_paths = []
    for pid in range(17):
        participant_plot_dir = os.path.join(ANALYSIS_PLOT_DIR, str(pid))
        if os.path.exists(participant_plot_dir):
            file_names = list_files(participant_plot_dir)
            for name in file_names:
                if name.endswith('raw.png'):
                    heatmap_paths.append(find_file_in_dir(name, participant_plot_dir))
    return heatmap_paths


if __name__ == '__main__':
    overwrite = True
    chse_extractor = ConcurrentHeatSourceEliminationExtractor(overwrite)
    hse_extractor = HeatSourceEliminationExtractor(overwrite)
    uvs_extractor = UnivariateSplineExtractor(overwrite)
    bvs_extractor = BivariateSplineExtractor(overwrite)
    extractors = [chse_extractor, hse_extractor, bvs_extractor]

    heatmap_paths = get_saliency_map_paths()
    #heatmap_paths = get_observation_heatmap_paths()
    compare_extractors(extractors, heatmap_paths)
