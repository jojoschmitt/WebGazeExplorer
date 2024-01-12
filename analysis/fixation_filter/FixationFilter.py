import os.path
import subprocess

from analysis.AnalysisConfiguration import AnalysisConfiguration
from analysis.analysis_utils import get_movements_file_path
from analysis.fixation_filter.tobiidata_to_uxidata import convert_tobiidata_to_uxidata
from config import ANALYSIS_DATA_DIR
from util import repo_root


class FixationFilter:
    def __init__(self, config):
        self.config: AnalysisConfiguration = config
        self.GAZE_TOOLKIT_RELEASE_DIR = os.path.join(repo_root, "analysis", "fixation_filter", "Release")
        self.IVT_EXE_PATH = os.path.join(self.GAZE_TOOLKIT_RELEASE_DIR, "i-vt.exe")

    def apply_ivt_fixation_filter(self):
        if not os.path.exists(self.IVT_EXE_PATH):
            raise FileNotFoundError(f'I-VT fixation filter executable could not be found ({self.IVT_EXE_PATH})'
                                    f'\nPlease make sure to provide the release binaries of the GazeToolkit '
                                    f'at the following location: {self.GAZE_TOOLKIT_RELEASE_DIR}')

        for pid in self.config.participants:
            movements_file_path = get_movements_file_path(pid)
            if not os.path.exists(movements_file_path) or self.config.general_overwrite:
                print(f"Applying I-VT fixation filter for participant {pid}")
                participant_data_dir = os.path.join(ANALYSIS_DATA_DIR, str(pid))
                input_file_path = os.path.join(participant_data_dir, "uxi_data.csv")
                if not os.path.exists(input_file_path):
                    print(f"UXI data file for participant {pid} not found, trying to create one ({input_file_path})")
                    if not convert_tobiidata_to_uxidata(participant_data_dir):
                        raise FileNotFoundError(f"UXI data file for participant {pid} could not be created")
                    print(f"Successfully created UXI data file for participant {pid}")
                output_file_path = os.path.join(participant_data_dir, "movements.csv")

                command = [
                    self.IVT_EXE_PATH,
                    input_file_path,
                    '--timestamp-format', 'ticks:us',
                    '--frequency', '120',
                    '--fillin', '--fillin-max-gap', '75',
                    '--select', 'Average',
                    '--threshold', '30',
                    '--merge', '--merge-max-gap', '75', '--merge-max-angle', '0.5',
                    '--discard', '--discard-min-duration', '60',
                    '--output', output_file_path
                ]

                subprocess.run(command, check=True)

                print(f"Successful application of I-VT fixation filter for participant {pid}")
