import os.path
import shutil
from datetime import datetime

from analysis.Plotter import Plotter
from analysis.Accumulator import Accumulator
from analysis.AccumulationMapping import AccumulationMapping
from analysis.AnalysisConfiguration import AnalysisConfiguration
from analysis.Differentiator import Differentiator
from analysis.Validator import Validator
from analysis.WeightType import WeightType
from analysis.analysis_utils import get_participant_analysis_data_dir, get_participant_experiment_data_dir, \
    get_movements_file_path, get_explorations_file_path
from analysis.fixation_filter.FixationFilter import FixationFilter


class Analyzer:
    def __init__(self, config, debug=False):
        self.t0 = None
        self.debug: bool = debug
        self.config: AnalysisConfiguration = config
        self.fixation_filter = None
        self.differentiator = None
        self.plotter = None
        self.accumulator = None
        self.validator = None
        self.initialize_components()

    def initialize_components(self):
        self.fixation_filter = FixationFilter(self.config)
        self.differentiator = Differentiator(self.config)
        self.plotter = Plotter(self.config)
        self.accumulator = Accumulator(self.config, self.plotter)
        self.validator = Validator(self.config, self.accumulator, self.plotter)

    def run(self):
        print(f"Starting analysis for participants: {self.config.participants}")
        self.t0 = datetime.now()

        self.import_observation_data()

        self.fixation_filter.apply_ivt_fixation_filter()

        self.analysis_data_for_participants_available()

        if self.config.saliency:
            self.differentiator.create_difference_fixations()

        self.plotter.plot_analysis_images()

        relatable_fixations = self.accumulator.get_relatable_fixations()
        relatable_fixations_map = self.accumulator.map_relatable_fixations(relatable_fixations)

        self.accumulator.generate_accumulated_fixations(relatable_fixations_map)

        self.accumulator.generate_directed_masks(relatable_fixations)

        accumulated_directed_masks = self.accumulator.generate_accumulated_directed_masks(relatable_fixations_map)

        self.plotter.plot_directed_heatmaps(relatable_fixations_map, accumulated_directed_masks)

        self.validator.leave_one_out_cross_validation(relatable_fixations_map)
        mapped_dm_correlations, mapped_hm_correlations, mapped_average_correlations = self.validator.analyse_cross_validation_results(relatable_fixations_map)

        self.plotter.save_cross_validation_analysis_results(
            mapped_dm_correlations,
            mapped_hm_correlations,
            mapped_average_correlations)

        print(self.time_running())

    def import_observation_data(self):
        tobii_data_str = "tobii_data.tsv"
        explorations_str = "explorations.tsv"
        for pid in self.config.participants:
            participant_experiment_data_dir = get_participant_experiment_data_dir(pid)
            if not os.path.exists(participant_experiment_data_dir):
                print(f"Experiment data directory for participant {pid} not found, skipping participant")
                continue
            experiment_tobii_data_path = os.path.join(participant_experiment_data_dir, tobii_data_str)
            assert os.path.exists(experiment_tobii_data_path)
            experiment_explorations_path = os.path.join(participant_experiment_data_dir, explorations_str)
            assert os.path.exists(experiment_explorations_path)
            participant_analysis_data_dir = get_participant_analysis_data_dir(pid)
            if not os.path.exists(participant_analysis_data_dir):
                os.mkdir(participant_analysis_data_dir)
            analysis_tobii_data_path = os.path.join(participant_analysis_data_dir, tobii_data_str)
            if not os.path.exists(analysis_tobii_data_path) or self.config.general_overwrite:
                try:
                    shutil.copy(experiment_tobii_data_path, analysis_tobii_data_path)
                except Exception as e:
                    print(f"Encountered an error while importing an Tobii data file: {e}")
            analysis_explorations_path = os.path.join(participant_analysis_data_dir, explorations_str)
            if not os.path.exists(analysis_explorations_path) or self.config.general_overwrite:
                try:
                    shutil.copy(experiment_explorations_path, analysis_explorations_path)
                except Exception as e:
                    print(f"Encountered an error while importing an explorations file: {e}")

    def analysis_data_for_participants_available(self):
        """Check if participant data directory, fixations and explorations file is available.
        """
        for pid in self.config.participants:
            participant_data_dir = get_participant_analysis_data_dir(pid)
            if not os.path.exists(participant_data_dir):
                raise FileNotFoundError(participant_data_dir)
            movements_file_path = get_movements_file_path(pid)
            if not os.path.exists(movements_file_path):
                raise FileNotFoundError(movements_file_path)
            explorations_file_path = get_explorations_file_path(pid)
            if not os.path.exists(explorations_file_path):
                raise FileNotFoundError(explorations_file_path)

    def time_running(self):
        assert self.t0 is not None
        return datetime.now() - self.t0


def get_default_analyzer():
    config = AnalysisConfiguration(
        participants=[i for i in range(1, 17)],
        general_overwrite=True,
        accumulation_overwrite=False,
        directed_mask_overwrite=False,
        validation_overwrite=False,
        saliency=False,
        accumulation_mapping=AccumulationMapping.TASK,
        accumulated_weight_type=WeightType.INTENSITY,  # Will always include intensity based accumulated heatmaps
        directed_weight_type=WeightType.ORDER
    )

    analyzer = Analyzer(config, debug=True)
    return analyzer


if __name__ == '__main__':
    """
    Accumulated directed masks are stored in one place disregarding the saliency flag.
    Heatmaps and scanpaths will be stored at different places regarding the saliency flag.
    
    The relatable_fixations (used for accumulation) parses fixations either from a salience
    considered fixations file or a non salience considered fixations file. 
    """

    config = AnalysisConfiguration(
        participants=[i for i in range(1, 3)],
        general_overwrite=True,
        accumulation_overwrite=False,
        directed_mask_overwrite=False,
        validation_overwrite=False,
        saliency=False,
        accumulation_mapping=AccumulationMapping.TASK,
        accumulated_weight_type=WeightType.INTENSITY,  # Will always include intensity based accumulated heatmaps
        directed_weight_type=WeightType.ORDER
    )

    analyzer = Analyzer(config, debug=True)
    analyzer.run()
