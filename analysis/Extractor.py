import os
from datetime import datetime
from abc import ABC, abstractmethod

from analysis.HeatPoint import heat_points_from_file, heat_points_to_file


class Extractor(ABC):
    """
    Interface for extracting all heat sources from a heatmap.
    """
    def __init__(self, overwrite=False):
        self.overwrite = overwrite
        self.heatmap_path = None
        self.t0 = None
        self.heat_sources = None
        self.heat_sources_file_path = None

    def get_heat_sources_from_heatmap(self, heatmap_path):
        self.heatmap_path = heatmap_path
        extraction_necessary = self._pre_extraction()
        if extraction_necessary:
            self._extract_heat_sources_from_heatmap()
            self._post_extraction()
        return self.heat_sources

    @abstractmethod
    def _extract_heat_sources_from_heatmap(self):
        pass

    def _pre_extraction(self):
        heatmap_parent_dir = os.path.dirname(self.heatmap_path)
        heat_source_file_dir = os.path.join(heatmap_parent_dir, "extracted_heat_sources")
        if not os.path.exists(heat_source_file_dir):
            os.mkdir(heat_source_file_dir)
        heatmap_name = ".".join(os.path.basename(self.heatmap_path).split(".")[:-1])
        self.heat_sources_file_path = os.path.join(heat_source_file_dir, f"{heatmap_name}-heat-sources.csv")
        if os.path.exists(self.heat_sources_file_path) and not self.overwrite:
            print(f"Reading heat sources from file {self.heat_sources_file_path}")
            self.heat_sources = heat_points_from_file(self.heat_sources_file_path)
            extraction_necessary = False
        else:
            self.heat_sources = []
            extraction_necessary = True
            print(f"Extracting heat sources from heatmap...")
            self.t0 = datetime.now().timestamp()
        return extraction_necessary

    def _post_extraction(self):
        time_delta = datetime.now().timestamp() - self.t0
        print(f"Extracted {len(self.heat_sources)} heat sources in {time_delta} seconds")
        # plot_points_on_img(heat_sources, heatmap_path)
        heat_points_to_file(self.heat_sources, self.heat_sources_file_path)
